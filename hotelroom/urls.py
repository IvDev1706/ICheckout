from django.urls import path
from .views import *

#patrones de ruta
urlpatterns = [
    path("",IndexView.as_view()),
    path("<int:id>/",RoomView.as_view()),
    path("type/<int:id>/",TypeView.as_view()),
]
