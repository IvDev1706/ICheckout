from django.views import View
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..services import BookingService
from ..forms import BookingDropForm, BookingModifyForm, BookingModifyStatusForm
from ..constants import BOOOKING_STATES

#vista principal
class BookingView(View):
    #atributos
    template_name = "booking.html"
    service = BookingService()
    drop_form = BookingDropForm
    modify_form = BookingModifyForm
    modify_status_form = BookingModifyStatusForm
    
    #metodo get
    def get(self, request:HttpRequest, id:int, *args, **kargs):
        #obtener reserva
        booking = self.service.get_booking(id)
        booking_copy = booking.copy()
        booking_copy.pop("state")
        booking_copy.pop("rooms")
        
        #preparar contexto
        context = {
            "title": "ICheckout - Reservas",
            "subtitle": "ICheckout - Reservas",
            "booking": booking,
            "drop_form": self.drop_form(initial={
                "id": id
            }),
            "modify_status_form": self.modify_status_form(initial={
                "id": id,
                "state": BOOOKING_STATES.index(booking["state"])
            }),
            "modify_form": self.modify_form(initial=booking_copy)
        }
        
        #retorno de plantilla
        return render(request,self.template_name,context)
    
    #metodo post
    def post(self, request:HttpRequest, id:int, *args, **kargs):
        #obtener operacion
        operation = request.POST.get("operation")
        
        #cargar formulario correspondiente
        form = None
        match operation:
            case "drop":
                form = self.drop_form(request.POST)
            case "modify":
                form = self.modify_form(request.POST)
            case "modify_status":
                form = self.modify_status_form(request.POST)
                
        #validar formulario
        if form.is_valid():
            #realizar operacion
            match operation:
                case "drop":
                    self.service.delete_booking(id)
                case "modify":
                    self.service.update_booking_info(form.cleaned_data)
                case "modify_status":
                    self.service.update_booking_status(form.cleaned_data)
        
        #redirigir a vista
        return redirect(f"/booking/{id}")