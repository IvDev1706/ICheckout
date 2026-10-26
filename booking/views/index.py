from django.views import View
from django.http import HttpRequest
from django.shortcuts import render
from ..services import BookingService

#vista principal
class IndexView(View):
    #atributos
    template_name = "index_booking.html"
    service = BookingService()
    
    #metodo get
    def get(self, request:HttpRequest, *args, **kargs):
        #obtener pagina
        page = int(request.GET.get("page",0))
        page = page if page < 1 else 1
        
        #preparar contexto
        context = {
            "title": "ICheckout - Reservas",
            "subtitle": "ICheckout - Reservas",
            "bookings": self.service.get_bookings(page),
        }
        
        #retorno de plantilla
        return render(request,self.template_name,context)