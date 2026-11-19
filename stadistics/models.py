from django.db import models
from hotelroom.models import HotelRoom

#ejecucion del calculo de prediccion de reservas
class ForecastRun(models.Model):
    #datos de la ejecucion
    created_at = models.DateTimeField(auto_now_add=True)
    model = models.CharField(max_length=40)
    history_start = models.DateField()
    history_end = models.DateField()
    horizon = models.IntegerField()
    rmse = models.FloatField(null=True)

    class Meta:
        ordering = ["-created_at"]

#punto de la serie historica o de la prediccion
class ForecastPoint(models.Model):
    #datos del punto
    run = models.ForeignKey(
        ForecastRun,
        on_delete=models.CASCADE,
        related_name="points"
    )
    period = models.DateField(db_index=True)
    value = models.FloatField()
    lower = models.FloatField(null=True)
    upper = models.FloatField(null=True)
    is_future = models.BooleanField(default=False)

    class Meta:
        ordering = ["period"]

#ejecucion del calculo de clustering de habitaciones
class ClusterRun(models.Model):
    #datos de la ejecucion
    created_at = models.DateTimeField(auto_now_add=True)
    algorithm = models.CharField(max_length=40, default="kmeans")
    clusters = models.IntegerField()
    inertia = models.FloatField(null=True)
    silhouette = models.FloatField(null=True)
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        ordering = ["-created_at"]

#patron detectado por el clustering
class ClusterGroup(models.Model):
    #datos del grupo
    run = models.ForeignKey(
        ClusterRun,
        on_delete=models.CASCADE,
        related_name="groups"
    )
    position = models.IntegerField()
    label = models.CharField(max_length=40)
    size = models.IntegerField()
    #promedios de las caracteristicas del grupo
    avg_bookings = models.FloatField()
    avg_guests = models.FloatField()
    avg_revenue = models.FloatField()
    avg_utilization = models.FloatField()

    class Meta:
        ordering = ["position"]

#habitacion asignada a un patron
class ClusterRoom(models.Model):
    #datos de la habitacion dentro del grupo
    group = models.ForeignKey(
        ClusterGroup,
        on_delete=models.CASCADE,
        related_name="rooms"
    )
    room = models.ForeignKey(HotelRoom, on_delete=models.CASCADE)
    bookings = models.IntegerField()
    guests = models.FloatField()
    revenue = models.FloatField()
    utilization = models.FloatField()

    class Meta:
        ordering = ["room__id"]
