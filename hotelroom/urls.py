from django.urls import path
from .views import *

#patrones de ruta
urlpatterns = [
    path("",IndexView.as_view()),
    path("create/",CreateView.as_view())
]
