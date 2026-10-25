import django.views as views
from django.shortcuts import render, redirect
from django.http import HttpRequest
from ..models import HotelRoom
from ..forms import HotelRoomDropForm, HotelRoomModifyForm
from ..services import HotelRoomService, ROOM_STATES

#vista de habitacion
class RoomView(views.View):
    #atributos
    template_name = "room.html"
    drop_form = HotelRoomDropForm
    modify_form = HotelRoomModifyForm
    service = HotelRoomService()
    
    #peticiones get
    def get(self, request:HttpRequest, id:int, *args, **kagrs):
        #obtener el objeto
        room = HotelRoom.objects.get(id=id)
        
        #contexto
        context = {
            "title": "ICheckout - Habitación",
            "subtitle": "ICheckout - Habitación",
            "room": {
                "pk": room.pk,
                "floor": room.floor,
                "type": room.type,
                "state": ROOM_STATES[room.state]
            },
            "drop_form": self.drop_form(initial={"id":id}),
            "modify_form": self.modify_form(initial={
                "id": id,
                "floor": room.floor,
                "type": room.type
            })
        }
        
        #renderizar plantilla
        return render(request,self.template_name,context)
    
    #peticiones post
    def post(self, request:HttpRequest, id:int, *args, **kagrs):
        #obtener operacion
        operation = request.POST.get("operation")
        
        #obtener formulario
        form = self.drop_form(request.POST) if operation == "drop" else self.modify_form(request.POST)
        
        #validar formulario
        if form.is_valid():
            #obeter operacion
            operation = form.cleaned_data.get("operation")
            
            #si es eliminar
            if operation == "drop":
                #eliminar objeto
                self.service.delete_room(id)
            elif operation == "modify":
                #actualiza el objeto
                self.service.update_room(form.cleaned_data)
        
        #validar operacion
        if operation == "modify":
            return redirect(f"/room/{id}")
        else:
            return redirect(f"/room/")