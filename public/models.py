from django.db import models

# Create your models here.
class ICUser(models.Model):
    #campos de usuario
    name = models.TextField(
        max_length=15,
        unique=True,
        db_index=True
    )
    password = models.TextField(
        max_length=256,
        null=False
    )
    role = models.TextField(
        max_length=15,
        null=False
    )