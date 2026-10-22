from django.views import View
from django.http import HttpRequest
from django.shortcuts import render
from ..models import ICUser

#vista de login
class ProfileView(View):
    #atributos
    template_name = "profile.html"
    
    #peticiones get
    def get(self, request:HttpRequest, *args, **kargs):
        #obtener datos de sesion
        user_id = request.session.get("user_id")
        
        #preparar contexto
        context = {
            "title": "ICheckout - Perfil",
            "user": ICUser.objects.get(id=user_id)
        }
        
        #renderizar la plantilla
        return render(request,self.template_name,context)