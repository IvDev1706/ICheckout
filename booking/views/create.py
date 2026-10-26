from django.views import View
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..services import BookingService
from ..forms import BookingAddForm

#vista principal
class CreateView(View):
    #atributos
    template_name = "create.html"
    form = BookingAddForm
    service = BookingService()
    
    #metodo get
    def get(self, request:HttpRequest, *args, **kargs):
        #preparar contexto
        context = {
            "title": "ICheckout - Reservas",
            "subtitle": "ICheckout - Reservas",
            "form": self.form()
        }
        
        #retorno de plantilla
        return render(request,self.template_name,context)
    
    #metodo post
    def post(self, request:HttpRequest, *args, **kargs):
        #obtener datos
        form = self.form(request.POST)
        
        #validar formulario
        if form.is_valid():
            #registrar reserva
            self.service.create_booking(form.cleaned_data)
            
        #redirigir a pagina
        return redirect("/booking/")