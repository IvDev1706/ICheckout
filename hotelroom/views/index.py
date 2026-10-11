import django.views as views
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..forms import RoomTypeAddForm, HotelRoomAddForm
from ..services import RoomTypeService, HotelRoomService

#vista principal de hotel
class IndexView(views.View):
    #plantilla de vista
    template_name = "index.html"
    type_form_class = RoomTypeAddForm
    room_form_class = HotelRoomAddForm
    type_service = RoomTypeService()
    room_service = HotelRoomService()
    
    #metodo get
    def get(self, request:HttpRequest, *args, **kargs):
        #obtener registros
        rooms = self.room_service.get_rooms()
        types = self.type_service.get_types()
        
        #contexto
        context = {
            "title": "ICheckout - Habitaciónes",
            "type_form": self.type_form_class(),
            "room_form": self.room_form_class(),
            "rooms": rooms,
            "types": types
        }
        
        #renderizar plantilla
        return render(request,self.template_name,context)
    
    def post(self, request:HttpRequest, *args, **kargs):
        #obtener datos en formulario
        form = self.type_form_class(request.POST)
        
        #guardar datos
        if form.is_valid():
            #guardar tipo en bd
            self.type_service.create_type(form.cleaned_data)
        
        #redirigir a index (get)
        return redirect("/room/")