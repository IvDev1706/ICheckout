from django.urls import path
from .views import *

#rutas
app_name = "stadistics"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("report/", ReportView.as_view(), name="report")
]
