from django.urls import path
from .views import *

#rutas de la app
urlpatterns = [
    path("",LoginView.as_view())
]
