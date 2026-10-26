from django.views import View
from django.http import HttpRequest
from django.shortcuts import render
from ..services import BookingService

#vista principal
class BookingView(View):
    #atributos
    template_name = "booking.html"
    service = BookingService()
    
    #metodo get
    def get(self, request:HttpRequest, id:int, *args, **kargs):
        #preparar contexto
        context = {
            "title": "ICheckout - Reservas",
            "subtitle": "ICheckout - Reservas",
            "booking": self.service.get_booking(id)
        }
        
        #retorno de plantilla
        return render(request,self.template_name,context)