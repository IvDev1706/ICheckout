import django.views as views
from django.shortcuts import render, redirect
from django.http import HttpRequest
from ..forms import RoomTypeDropForm, RoomTypeModifyForm
from ..services import RoomTypeService

#vista de habitacion
class TypeView(views.View):
    #atributos
    template_name = "type.html"
    drop_form = RoomTypeDropForm
    modify_form = RoomTypeModifyForm
    service = RoomTypeService()
    
    #peticiones get
    def get(self, request:HttpRequest, id:int, *args, **kagrs):
        #obtener el objeto
        room = self.service.get_type(id)
        
        #contexto
        context = {
            "title": "ICheckout - Habitación",
            "subtitle": "ICheckout - Habitación",
            "type": {
                "pk": room.pk,
                "name": room.name,
                "price": room.price
            },
            "drop_form": self.drop_form(initial={"id":id}),
            "modify_form": self.modify_form(initial={
                "id": id,
                "name": room.name,
                "price": room.price
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
                self.service.delete_type(id)
            elif operation == "modify":
                #actualiza el objeto
                self.service.update_type(form.cleaned_data)
        
        #validar operacion
        if operation == "modify":
            return redirect(f"/room/type/{id}")
        else:
            return redirect(f"/room/")