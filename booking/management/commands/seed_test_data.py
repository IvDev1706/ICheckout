import random
from calendar import monthrange
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from booking.constants import BOOOKING_STATES, TOURIST_TYPES
from booking.models import Booking, BookingRoomAsignment
from hotelroom.models import HotelRoom, RoomType
from icheckout.settings import FLOORS, ROOMS_PER_FLOOR
from public.models import ICUser
from public.services import UserService

# datos de los usuarios de prueba
USERS = [
    {"name": "recepcion", "password": "Recepcion123!", "role": "recepcionista"},
    {"name": "analista", "password": "Analista123!", "role": "Analista"},
]

# tipos de habitacion (nombre, precio, porcentaje del hotel)
ROOM_TYPES = [
    ("Regular", 850.0, 0.60),
    ("VIP", 1600.0, 0.30),
    ("Suite", 3200.0, 0.10),
]

# nombres de huespedes para las reservas
OWNERS = [
    "Juan Perez", "Maria Lopez", "Carlos Ramirez", "Ana Torres",
    "Luis Hernandez", "Sofia Martinez", "Jorge Diaz", "Laura Gomez",
    "Pedro Sanchez", "Elena Cruz", "Miguel Flores", "Paula Rojas",
    "Ricardo Vargas", "Daniela Castro", "Alberto Mendoza", "Lucia Ortega",
    "Fernando Rios", "Gabriela Nunez", "Hector Salazar", "Valeria Pineda",
    "Andres Guzman", "Camila Herrera", "Raul Espinoza", "Monica Ibarra",
    "Diego Aguilar", "Patricia Molina", "Oscar Delgado", "Renata Fuentes",
    "Arturo Cabrera", "Isabel Cano", "Emilio Pacheco", "Natalia Solis",
    "Sergio Beltran", "Adriana Rivas", "Martin Cordero", "Claudia Mejia",
    "Ivan Zavala", "Rosa Trejo", "Pablo Lara", "Teresa Acosta",
    "Ramon Quintero", "Julia Palacios", "Marco Villalobos", "Silvia Serrano",
    "Enrique Valle", "Brenda Escobar", "Tomas Cervantes", "Lorena Bautista",
    "Julio Andrade", "Veronica Peña",
]

# estados de reserva
RESERVADA, EN_CASA, TERMINADA, CANCELADA = range(len(BOOOKING_STATES))


class Command(BaseCommand):
    help = "Puebla la base de datos con usuarios, habitaciones y reservas de prueba."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Borra los datos existentes de usuarios, habitaciones y reservas antes de poblar.",
        )

    def handle(self, *args, **options):
        if not options["force"] and (
            ICUser.objects.exists()
            or HotelRoom.objects.exists()
            or RoomType.objects.exists()
            or Booking.objects.exists()
        ):
            self.stdout.write(self.style.WARNING(
                "La base de datos ya tiene informacion. Use --force para reemplazarla."
            ))
            return

        if options["force"]:
            self._reset_tables()
            self.stdout.write("Datos anteriores eliminados y contadores reiniciados.")

        with transaction.atomic():
            rng = random.Random(42)

            self._seed_users()
            types = self._seed_room_types()
            rooms = self._seed_rooms(rng, types)
            self._seed_bookings(rng, rooms)

        self.stdout.write(self.style.SUCCESS("Datos de prueba creados correctamente."))
        self.stdout.write(f"  usuarios: {ICUser.objects.count()}")
        self.stdout.write(f"  tipos de habitacion: {RoomType.objects.count()}")
        self.stdout.write(f"  habitaciones: {HotelRoom.objects.count()}")
        self.stdout.write(f"  reservas: {Booking.objects.count()}")
        self.stdout.write(f"  asignaciones: {BookingRoomAsignment.objects.count()}")

    def _reset_tables(self):
        # vaciar tablas y reiniciar el AUTO_INCREMENT para que los ids empiecen en 1
        models = [BookingRoomAsignment, Booking, HotelRoom, RoomType, ICUser]

        with connection.cursor() as cursor:
            if connection.vendor == "mysql":
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        for model in models:
            model.objects.all().delete()

        with connection.cursor() as cursor:
            if connection.vendor == "mysql":
                for model in models:
                    cursor.execute(
                        f"ALTER TABLE `{model._meta.db_table}` AUTO_INCREMENT = 1"
                    )
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            elif connection.vendor == "sqlite":
                for model in models:
                    cursor.execute(
                        "DELETE FROM sqlite_sequence WHERE name = %s",
                        [model._meta.db_table],
                    )

    def _seed_users(self):
        service = UserService()
        for user in USERS:
            service.create_user(user)
            self.stdout.write(f"Usuario creado: {user['name']} ({user['role']})")

    def _seed_room_types(self):
        types = {}
        for name, price, _ in ROOM_TYPES:
            types[name] = RoomType.objects.create(name=name, price=price)
        return types

    def _seed_rooms(self, rng, types):
        total = FLOORS * ROOMS_PER_FLOOR

        # cantidad exacta por tipo segun los porcentajes definidos
        names = [name for name, _, _ in ROOM_TYPES]
        distribution = []
        for name, _, share in ROOM_TYPES:
            distribution.extend([name] * int(round(total * share)))
        # ajustar por redondeo hasta cubrir todas las habitaciones
        while len(distribution) < total:
            distribution.append(names[0])
        distribution = distribution[:total]

        rng.shuffle(distribution)

        rooms = []
        index = 0
        for floor in range(1, FLOORS + 1):
            for _ in range(ROOMS_PER_FLOOR):
                rooms.append(HotelRoom.objects.create(
                    floor=floor,
                    state=0,
                    type=types[distribution[index]],
                ))
                index += 1
        return rooms

    def _seed_bookings(self, rng, rooms):
        today = date.today()
        year = today.year

        # 50 reservas repartidas en los 12 meses del año
        # (4 por mes + 2 que estan en casa hoy)
        arrive_dates = []
        for month in range(1, 13):
            last_day = monthrange(year, month)[1]
            for _ in range(4):
                arrive_dates.append(date(year, month, rng.randint(1, last_day)))
        arrive_dates.extend([today - timedelta(days=1), today])
        rng.shuffle(arrive_dates)

        type_names = [name for name, _, _ in ROOM_TYPES]
        type_weights = [share for _, _, share in ROOM_TYPES[:2]]
        type_weights.append(1 - sum(type_weights))

        rooms_by_type = {}
        for room in rooms:
            rooms_by_type.setdefault(room.type.name, []).append(room)

        # intervalos ocupados por habitacion para evitar traslapes
        occupied = {room.pk: [] for room in rooms}

        for arrive in arrive_dates:
            nights = rng.randint(2, 5)
            departure = arrive + timedelta(days=nights)

            # definir estado de la reserva segun la fecha
            if arrive > today:
                state = CANCELADA if rng.random() < 0.10 else RESERVADA
            elif departure > today:
                state = EN_CASA
            else:
                state = CANCELADA if rng.random() < 0.12 else TERMINADA

            guests = rng.choices([1, 2, 3, 4, 5], weights=[30, 35, 20, 10, 5])[0]

            booking = Booking.objects.create(
                arrive_date=arrive,
                departure_date=departure if state == TERMINADA else None,
                guests=guests,
                state=state,
                tourist_type=rng.randint(0, len(TOURIST_TYPES) - 1),
                owner=rng.choice(OWNERS),
            )

            # una habitacion por reserva, dos si el grupo es grande
            room_count = 2 if guests > 4 else 1
            assigned = []
            for _ in range(room_count):
                room = self._pick_room(
                    rng, rooms_by_type, type_names, type_weights,
                    occupied, arrive, departure, assigned,
                )
                if room is None:
                    break
                BookingRoomAsignment.objects.create(booking=booking, room=room)
                occupied[room.pk].append((arrive, departure))
                assigned.append(room.pk)

        # estado final de cada habitacion segun sus reservas activas
        # (ocupada tiene prioridad sobre reservada)
        HotelRoom.objects.all().update(state=0)
        room_states = {}
        for assignment in BookingRoomAsignment.objects.select_related("booking"):
            state = assignment.booking.state
            if state == EN_CASA:
                room_states[assignment.room_id] = 2
            elif state == RESERVADA and room_states.get(assignment.room_id, 0) < 2:
                room_states[assignment.room_id] = 1

        for room_id, state in room_states.items():
            HotelRoom.objects.filter(pk=room_id).update(state=state)

    def _pick_room(self, rng, rooms_by_type, type_names, type_weights,
                   occupied, arrive, departure, excluded):
        preferred = rng.choices(type_names, weights=type_weights)[0]

        def candidates(type_name):
            available = []
            for room in rooms_by_type.get(type_name, []):
                if room.pk in excluded:
                    continue
                if any(
                    arrive < end and start < departure
                    for start, end in occupied[room.pk]
                ):
                    continue
                available.append(room)
            return available

        available = candidates(preferred)
        if available:
            return rng.choice(available)

        # buscar en cualquier tipo disponible
        for type_name in type_names:
            if type_name == preferred:
                continue
            available = candidates(type_name)
            if available:
                return rng.choice(available)

        return None
