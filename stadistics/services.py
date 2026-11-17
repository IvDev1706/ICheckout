from calendar import monthrange
from datetime import date
from django.db.models import Count, Max, Min
from booking.constants import BOOOKING_STATES, TOURIST_TYPES
from booking.models import Booking, BookingRoomAsignment

#servicio de estadisticas
class StatisticsService:
    #obtener los años con reservas registradas
    def get_years(self):
        #manejo de error
        try:
            #obtener fechas limite
            limits = Booking.objects.aggregate(
                first=Min("arrive_date"),
                last=Max("arrive_date")
            )
            
            #incluir siempre el año actual
            current_year = date.today().year
            years = {current_year}
            
            #agregar el rango de años con informacion
            if limits["first"] and limits["last"]:
                years.update(range(limits["first"].year, limits["last"].year + 1))
            
            #retornar años de mas reciente a mas antiguo
            return sorted(years, reverse=True)
        except Exception as e:
            #mensaje de error
            print(f"Error: {e}")
            
            #retornar solo el año actual
            return [date.today().year]
    
    #obtener todas las metricas del periodo
    def get_report(self, month:int, year:int):
        return {
            "tourist_types": self.get_tourist_types(month, year),
            "room_types": self.get_room_types(month, year),
            "bookings_per_day": self.get_bookings_per_day(month, year),
            "booking_states": self.get_booking_states(month, year),
        }
    
    #reservas del periodo para el reporte csv
    def get_bookings_report(self, month:int, year:int):
        #manejo de error
        try:
            #obtener reservas del periodo
            bookings = list(Booking.objects.filter(
                arrive_date__month=month,
                arrive_date__year=year
            ).order_by("arrive_date", "id"))
            
            #obtener habitaciones asignadas a las reservas
            assignments = BookingRoomAsignment.objects.filter(
                booking__in=bookings
            ).select_related("room").order_by("room__id")
            
            #agrupar habitaciones por reserva
            rooms_by_booking = {}
            for assignment in assignments:
                rooms_by_booking.setdefault(assignment.booking_id, []).append(
                    f"H-{assignment.room_id}"
                )
            
            #retornar filas del reporte
            return [{
                "pk": booking.pk,
                "arrive_date": booking.arrive_date.strftime("%d/%m/%Y"),
                "departure_date": booking.departure_date.strftime("%d/%m/%Y") if booking.departure_date else "",
                "guests": booking.guests,
                "state": BOOOKING_STATES[booking.state],
                "tourist_type": TOURIST_TYPES[booking.tourist_type],
                "owner": booking.owner,
                "rooms": ", ".join(rooms_by_booking.get(booking.pk, [])),
            } for booking in bookings]
        except Exception as e:
            #mensaje de error
            print(f"Error: {e}")
            
            #retornar vacio
            return []
    
    #reservas por tipo de turista en el periodo
    def get_tourist_types(self, month:int, year:int):
        #manejo de error
        try:
            #contar reservas por tipo
            rows = Booking.objects.filter(
                arrive_date__month=month,
                arrive_date__year=year
            ).values("tourist_type").annotate(total=Count("id"))
            
            #mapear resultados por indice
            counts = {row["tourist_type"]: row["total"] for row in rows}
            
            #mantener todas las categorias aunque esten en cero
            return {
                "labels": TOURIST_TYPES,
                "values": [counts.get(index, 0) for index in range(len(TOURIST_TYPES))]
            }
        except Exception as e:
            #mensaje de error
            print(f"Error: {e}")
            
            #retornar vacio
            return {"labels": [], "values": []}
    
    #reservas por tipo de habitacion en el periodo
    def get_room_types(self, month:int, year:int):
        #manejo de error
        try:
            #contar asignaciones de habitacion por tipo
            rows = BookingRoomAsignment.objects.filter(
                booking__arrive_date__month=month,
                booking__arrive_date__year=year
            ).values("room__type__name").annotate(total=Count("id")).order_by("-total")
            
            #retornar etiquetas y valores
            return {
                "labels": [row["room__type__name"] or "Sin tipo" for row in rows],
                "values": [row["total"] for row in rows]
            }
        except Exception as e:
            #mensaje de error
            print(f"Error: {e}")
            
            #retornar vacio
            return {"labels": [], "values": []}
    
    #reservas por dia del mes seleccionado
    def get_bookings_per_day(self, month:int, year:int):
        #manejo de error
        try:
            #contar reservas agrupadas por fecha de llegada
            rows = Booking.objects.filter(
                arrive_date__month=month,
                arrive_date__year=year
            ).values("arrive_date").annotate(total=Count("id"))
            
            #mapear resultados por dia
            counts = {row["arrive_date"].day: row["total"] for row in rows}
            
            #incluir todos los dias del mes aunque esten en cero
            days = monthrange(year, month)[1]
            return {
                "labels": [str(day) for day in range(1, days + 1)],
                "values": [counts.get(day, 0) for day in range(1, days + 1)]
            }
        except Exception as e:
            #mensaje de error
            print(f"Error: {e}")
            
            #retornar vacio
            return {"labels": [], "values": []}
    
    #reservas canceladas contra terminadas en el periodo
    def get_booking_states(self, month:int, year:int):
        #manejo de error
        try:
            #contar reservas por estado
            rows = Booking.objects.filter(
                arrive_date__month=month,
                arrive_date__year=year
            ).values("state").annotate(total=Count("id"))
            
            #mapear resultados por estado
            counts = {row["state"]: row["total"] for row in rows}
            
            #indices de los estados a comparar
            cancelled = BOOOKING_STATES.index("Cancelada")
            finished = BOOOKING_STATES.index("Terminada")
            
            #retornar solo canceladas y terminadas
            return {
                "labels": [BOOOKING_STATES[cancelled], BOOOKING_STATES[finished]],
                "values": [counts.get(cancelled, 0), counts.get(finished, 0)]
            }
        except Exception as e:
            #mensaje de error
            print(f"Error: {e}")
            
            #retornar vacio
            return {"labels": [], "values": []}
