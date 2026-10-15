from django.views import View
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..forms import LoginForm

#vista de login
class LoginView(View):
    #atributos
    template_name = "login.html"
    form = LoginForm
    
    #peticiones get
    def get(self, request:HttpRequest, *args, **kargs):
        #preparar contexto
        context = {
            "title": "ICheckout - Login",
            "form": self.form()
        }
        
        #renderizar la plantilla
        return render(request,self.template_name,context)
    
    #peticiones post (formularios)
    def post(self, request:HttpRequest, *args, **kargs):
        #obtener datos
        form = self.form(request.POST)
        
        #si es valido
        if form.is_valid():
            #validar credenciales
            pass
            
        #redirigir a login
        return redirect("/room/")