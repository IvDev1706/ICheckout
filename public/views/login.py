from django.views import View
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..forms import LoginForm
from ..services import UserService

#vista de login
class LoginView(View):
    #atributos
    template_name = "login.html"
    form = LoginForm
    service = UserService()
    
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
            #validar credenciales
            user_id = self.service.validate_user(form.cleaned_data)
            
            #validar usuario
            if user_id:
                #añadir sesion
                request.session["user_id"] = user_id
                #obtener y guardar rol
                u = self.service.get_user(user_id)
                request.session["user_role"] = u.role or ''
            
        #redirigir a login
        return redirect("/home/")