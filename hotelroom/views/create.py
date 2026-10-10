import django.views as views
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..forms import HotelRoomAddForm
from ..services import HotelRoomService

#vista principal de hotel
class CreateView(views.View):
    #plantilla de vista
    template_name = "create.html"
    form_class = HotelRoomAddForm
    service = HotelRoomService()
    
    #metodo get
    def get(self, request:HttpRequest, *args, **kargs):
        #contexto
        context = {
            "title": "Habitacion - Registro",
            "form": self.form_class()
        }
        
        #renderizar plantilla
        return render(request,self.template_name,context)
    
    def post(self, request:HttpRequest, *args, **kargs):
        #obtener datos en formulario
        form = self.form_class(request.POST)
        
        #guardar datos
        if form.is_valid():
            #guardar tipo en bd
            self.service.create_room(form.cleaned_data)
        
        #redirigir a index (get)
        return redirect("/room/")