import django.views as views
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..forms import HotelRoomModifyForm
from ..services import HotelRoomService

#vista de actualizacion
class UpdateView(views.View):
    #atributos
    template_name = "update.html"
    form = HotelRoomModifyForm
    service = HotelRoomService()
    
    #peticiones get (render de vista)
    def get(self, request, id:int, *args, **kargs):
        #obtener objeto
        room = self.service.get_room(id)
        
        #preparar contexto
        context = {
            "title": "ICheckout - Habitación",
            "id": room.pk,
            "form": self.form(initial={
                "id": room.pk,
                "floor": room.floor,
                "type": room.type,
                "state": room.state
            })
        }
        
        #retornar la plantilla
        return render(request, self.template_name, context)
    
    #peticiones post (recepcion de formularios)
    def post(self, request:HttpRequest, id:int, *args, **kargs):
        #obtencion de datos
        form_data = self.form(request.POST)
        
        #validar formulario
        if form_data.is_valid():
            #ejecutar operacion
            self.service.update_room(form_data.cleaned_data)
            
        #redirigir a la vista
        return redirect(f"/room/{id}")
    