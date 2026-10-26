from datetime import date
from django.db import models
from hotelroom.models import HotelRoom

#MOdelo de reserva
class Booking(models.Model):
    #campos del modelo
    arrive_date = models.DateField(
        null=False,
        db_index=True,
        default=date.today()
    )
    departure_date = models.DateField(
        null=True,
        db_index=True
    )
    guests = models.IntegerField(null=False)
    state = models.IntegerField(null=False,default=0)
    tourist_type = models.IntegerField(null=False)
    owner = models.CharField(
        max_length=30,
        null=False,
        db_index=True
    )
    
#asignacion de reserva
class BookingRoomAsignment(models.Model):
    #campos del modelo
    room = models.ForeignKey(
        HotelRoom,
        on_delete=models.CASCADE,
        null=False
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        null=False
    )