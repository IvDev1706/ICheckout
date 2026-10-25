from django.views import View
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..forms import SignUpForm
from ..services import UserService

#vista de sign up
class SignUpView(View):
    #atributos
    template_name = "signup.html"
    form = SignUpForm
    service = UserService()
    
    #peticiones get
    def get(self, request:HttpRequest, *args, **kargs):
        #preparar contexto
        context = {
            "title": "ICheckout - SignUp",
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
            #crear usuario
            self.service.create_user(form.cleaned_data)
            
        #redirigir a login
        return redirect("/")