from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..forms import LoginForm
from ..models import ICUser

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
            "form": self.form(),
            "layout": "login",
        }
        
        #renderizar la plantilla
        return render(request,self.template_name,context)
    
    #peticiones post (formularios)
    def post(self, request:HttpRequest, *args, **kargs):
        #obtener datos
        form = self.form(request.POST)
        
        #si es valido
        if form.is_valid():
            #manejo de error
            try:
                #validar credenciales
                u = ICUser.objects.get(
                    name=form.cleaned_data.get("name"),
                    password=form.cleaned_data.get("password")
                )
                
                #añadir sesion
                request.session["user_id"] = u.pk
            except ObjectDoesNotExist:
                pass
            
        #redirigir a login
        return redirect("/room/")