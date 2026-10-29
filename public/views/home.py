from django.views import View
from django.http import HttpRequest
from django.shortcuts import render
from ..constants import USER_MODULES, USER_ROLES

#vista home
class HomeView(View):
    #atributos
    template_name = "home.html"
    
    #metodo get
    def get(self, request:HttpRequest, *args, **kargs):
        #recuperar rol
        role = request.session.get("user_role")
        
        #preparar contexto
        context = {
            "title": "ICheckout - Principal",
            "subtitle": "ICheckout - Recepcion" if role == USER_ROLES[0] else "ICheckout - Estadisticas",
            "modules": USER_MODULES.get(role,[])
        }
        
        #retornar plantilla
        return render(request,self.template_name,context)