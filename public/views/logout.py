from django.views import View
from django.http import HttpRequest
from django.shortcuts import render

#vista de login
class LogoutView(View):
    #atributos
    template_name = "logout.html"
    
    #peticiones get
    def get(self, request:HttpRequest, *args, **kargs):
        #limpiamos la sesion
        request.session.flush()
        
        #preparar contexto
        context = {
            "title": "ICheckout - Logout",
            "subtitle": "ICheckout - Cierre de sesion"
        }
        
        #renderizar la plantilla
        return render(request,self.template_name,context)