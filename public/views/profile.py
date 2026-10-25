from django.views import View
from django.http import HttpRequest
from django.shortcuts import render
from ..services import UserService

#vista de login
class ProfileView(View):
    #atributos
    template_name = "profile.html"
    service = UserService()
    
    #peticiones get
    def get(self, request:HttpRequest, *args, **kargs):
        #obtener datos de sesion
        user_id = request.session.get("user_id")
        
        #preparar contexto
        context = {
            "title": "ICheckout - Perfil",
            "subtitle": "ICheckout - Perfil de usuario",
            "user": self.service.get_user(int(user_id))
        }
        
        #renderizar la plantilla
        return render(request,self.template_name,context)