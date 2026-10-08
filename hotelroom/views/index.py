import django.views as views
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..forms import RoomTypeAddForm
from ..models import RoomType, HotelRoom

#vista principal de hotel
class IndexView(views.View):
    #plantilla de vista
    template_name = "index.html"
    type_form_class = RoomTypeAddForm
    
    #metodo get
    def get(self, request:HttpRequest, *args, **kargs):
        #obtener registros
        rooms = HotelRoom.objects.order_by("-floor").all()
        types = RoomType.objects.all()
        
        #contexto
        context = {
            "title": "ICheckout - Habitación",
            "type_form": self.type_form_class(),
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
            RoomType.objects.create(
                name=form.cleaned_data.get("name"),
                price=form.cleaned_data.get("price")
            )
        
        #redirigir a index (get)
        return redirect("/room/")