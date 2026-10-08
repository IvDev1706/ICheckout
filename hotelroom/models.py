from django.db import models

#modelo de tipo de habitacion
class RoomType(models.Model):
    #campos de tipo habitacion
    name = models.TextField(
        max_length=15,
        unique=True,
        db_index=True,
        null=False
    )
    price = models.FloatField(null=False)
    
    def __str__(self):
        return self.name

#Modelo de habitacion
class HotelRoom(models.Model):
    #campos de habitacion
    floor = models.IntegerField(null=False)
    state = models.IntegerField(default=0)
    type = models.ForeignKey(
        RoomType,
        on_delete=models.SET_NULL,
        null=True
    )