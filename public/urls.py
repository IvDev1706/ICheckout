from django.urls import path
from .views import *

#rutas de la app
urlpatterns = [
    path("",LoginView.as_view()),
    path("profile/",ProfileView.as_view()),
    path("logout/",LogoutView.as_view()),
    path("signup/",SignUpView.as_view())
]
