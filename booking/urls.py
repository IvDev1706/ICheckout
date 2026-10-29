from django.urls import path
from .views import *

#rutas
urlpatterns = [
    path("",IndexView.as_view()),
    path("<int:id>/",BookingView.as_view())
]
