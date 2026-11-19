from datetime import date

import numpy as np
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from booking.models import BookingRoomAsignment
from hotelroom.models import HotelRoom
from stadistics.models import ClusterGroup, ClusterRoom, ClusterRun

# nombres de los patrones cuando se piden tres grupos
PATTERN_LABELS = ["Baja demanda", "Demanda media", "Alta demanda"]


class Command(BaseCommand):
    help = "Agrupa las habitaciones por patron de demanda con scikit-learn y guarda el resultado."

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            default=None,
            help="Año a analizar (default el año actual).",
        )
        parser.add_argument(
            "--clusters",
            type=int,
            default=3,
            help="Numero de grupos a detectar (default 3).",
        )

    def handle(self, *args, **options):
        year = options["year"] or date.today().year
        requested = options["clusters"]

        if requested < 2:
            raise CommandError("Se necesitan al menos 2 grupos (--clusters).")

        # periodo analizado
        start = date(year, 1, 1)
        end = date(year, 12, 31)
        days = (end - start).days + 1

        # habitaciones del hotel
        rooms = list(HotelRoom.objects.select_related("type"))
        if len(rooms) < 2:
            raise CommandError("Se necesitan al menos 2 habitaciones para agrupar.")

        # metricas acumuladas por habitacion
        stats = {
            room.pk: {"bookings": 0, "guests": 0, "revenue": 0.0, "nights": 0}
            for room in rooms
        }

        assignments = BookingRoomAsignment.objects.filter(
            booking__arrive_date__gte=start,
            booking__arrive_date__lte=end,
        ).select_related("booking", "room__type")

        for assignment in assignments:
            entry = stats.get(assignment.room_id)
            if entry is None:
                continue

            booking = assignment.booking

            # noches reservadas (minimo una)
            departure = booking.departure_date or booking.arrive_date
            nights = max((departure - booking.arrive_date).days, 1)

            entry["bookings"] += 1
            entry["guests"] += booking.guests
            entry["nights"] += nights

            price = assignment.room.type.price if assignment.room.type else 0.0
            entry["revenue"] += price * nights

        # caracteristicas: reservas, huespedes promedio, ingreso y ocupacion
        features = []
        for room in rooms:
            entry = stats[room.pk]
            count = entry["bookings"]
            features.append([
                count,
                entry["guests"] / count if count else 0.0,
                entry["revenue"],
                entry["nights"] / days,
            ])

        matrix = np.array(features, dtype=float)
        scaled = StandardScaler().fit_transform(matrix)

        # ajustar el numero de grupos a la cantidad de habitaciones
        clusters = min(requested, len(rooms) - 1)
        if clusters != requested:
            self.stdout.write(self.style.WARNING(
                f"Se ajustaron los grupos a {clusters} por la cantidad de habitaciones."
            ))

        # entrenar el modelo
        kmeans = KMeans(n_clusters=clusters, n_init=10, random_state=42).fit(scaled)

        # calidad de la separacion entre grupos
        silhouette = None
        try:
            silhouette = round(float(silhouette_score(scaled, kmeans.labels_)), 4)
        except Exception:
            silhouette = None

        # agrupar habitaciones por cluster
        groups = {}
        for label, room, values in zip(kmeans.labels_, rooms, features):
            groups.setdefault(int(label), []).append((room, values))

        # ordenar por ocupacion promedio para nombrar de menor a mayor
        ordered = sorted(
            groups.items(),
            key=lambda item: float(np.mean([values[3] for _, values in item[1]])),
        )

        # guardar el resultado reemplazando la ejecucion anterior
        with transaction.atomic():
            ClusterRun.objects.all().delete()
            run = ClusterRun.objects.create(
                algorithm="kmeans",
                clusters=clusters,
                inertia=round(float(kmeans.inertia_), 4),
                silhouette=silhouette,
                period_start=start,
                period_end=end,
            )

            for position, (_, members) in enumerate(ordered):
                values = np.array([values for _, values in members], dtype=float)
                avg_bookings = round(float(values[:, 0].mean()), 2)
                group = ClusterGroup.objects.create(
                    run=run,
                    position=position,
                    label=self._label(position, len(ordered), avg_bookings),
                    size=len(members),
                    avg_bookings=avg_bookings,
                    avg_guests=round(float(values[:, 1].mean()), 2),
                    avg_revenue=round(float(values[:, 2].mean()), 2),
                    avg_utilization=round(float(values[:, 3].mean()), 4),
                )

                ClusterRoom.objects.bulk_create([
                    ClusterRoom(
                        group=group,
                        room=room,
                        bookings=int(row[0]),
                        guests=round(float(row[1]), 2),
                        revenue=round(float(row[2]), 2),
                        utilization=round(float(row[3]), 4),
                    )
                    for room, row in members
                ])

        # resumen en consola
        self.stdout.write(self.style.SUCCESS("Clustering calculado correctamente."))
        self.stdout.write(f"  periodo: {start:%d/%m/%Y} - {end:%d/%m/%Y}")
        self.stdout.write(f"  habitaciones: {len(rooms)}")
        self.stdout.write(f"  grupos: {clusters} (silueta: {silhouette})")
        for group in run.groups.all():
            self.stdout.write(
                f"  {group.label}: {group.size} habitaciones "
                f"(ocupacion {group.avg_utilization:.2%}, "
                f"ingreso {group.avg_revenue:.2f}, "
                f"reservas {group.avg_bookings:.1f})"
            )

    # nombre del patron segun su posicion por ocupacion
    def _label(self, position: int, total: int, avg_bookings: float) -> str:
        if avg_bookings == 0:
            return "Sin actividad"
        if total == 1:
            return "Demanda media"
        if total == len(PATTERN_LABELS):
            return PATTERN_LABELS[position]
        if position == 0:
            return "Baja demanda"
        if position == total - 1:
            return "Alta demanda"
        return f"Demanda media {position}"
