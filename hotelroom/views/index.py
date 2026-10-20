import django.views as views
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..forms import RoomTypeAddForm, HotelRoomAddForm, HotelRoomPaginationForm
from ..services import RoomTypeService, HotelRoomService

#vista principal de hotel
class IndexView(views.View):
    #plantilla de vista
    template_name = "index.html"
    type_form_class = RoomTypeAddForm
    room_form_class = HotelRoomAddForm
    room_paginator_form_class = HotelRoomPaginationForm
    type_service = RoomTypeService()
    room_service = HotelRoomService()
    
    #metodo get
    def get(self, request:HttpRequest, *args, **kargs):
        #obtener el piso
        start_floor = int(request.GET.get("start_floor",1))
        span = int(request.GET.get("span",4))
        
        #obtener registros
        rooms = self.room_service.get_rooms(start_floor,span)
        types = self.type_service.get_types()
        
        #buscar el piso con mas habitaciones
        max_rooms = 0
        for floor in rooms:
            #comparar
            if len(floor) > max_rooms:
                #cambiar el maximo
                max_rooms = len(floor)
                
        gaps = [range(max_rooms - len(floor)) for floor in rooms]
            
        #contexto
        context = {
            "title": "ICheckout - Habitaciónes",
            "layout": "main",
            "type_form": self.type_form_class(),
            "room_form": self.room_form_class(),
            "room_paginator_form": self.room_paginator_form_class(),
            "rooms": [{"rooms": rooms[i], "gaps": gaps[i]} for i in range(len(rooms))],
            "types": types
        }
        
        #renderizar plantilla
        return render(request,self.template_name,context)
    
    def post(self, request:HttpRequest, *args, **kargs):
        #obtener el modelo
        model = request.POST.get("model")
        
        #obtener datos en formulario
        form = (
            self.type_form_class(request.POST) if model == "roomtype" 
                else self.room_paginator_form_class(request.POST) if model == "hotelroom__pagination"
                else self.room_form_class(request.POST)
        )
        
        #guardar datos
        if form.is_valid():
            if model == "roomtype":
                #guardar tipo en bd
                self.type_service.create_type(form.cleaned_data)
            elif model == "hotelroom":
                #guardar habitacion en bd
                self.room_service.create_room(form.cleaned_data)
            else:
                #obtener parametros
                start_floor = form.cleaned_data.get("start_floor")
                span = form.cleaned_data.get("span")
                
                #aplicar filtros
                return redirect(f"/room/?start_floor={start_floor}&span={span}")
        
        #redirigir a index (get)
        return redirect("/room/")