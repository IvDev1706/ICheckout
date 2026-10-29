from django.views import View
from django.http import HttpRequest
from django.shortcuts import render, redirect
from ..services import BookingService
from ..forms import BookingAddForm, BookingSearchForm

#vista principal
class IndexView(View):
    #atributos
    template_name = "index_booking.html"
    service = BookingService()
    form_type = BookingAddForm
    search_form_type = BookingSearchForm
    
    #metodo get
    def get(self, request:HttpRequest, *args, **kargs):
        #obtener pagina
        page = int(request.GET.get("page",0))
        page = page if page < 1 else 1
        
        #obtener busqueda
        search = request.GET.get("search","")
        
        #preparar contexto
        context = {
            "title": "ICheckout - Reservas",
            "subtitle": "ICheckout - Reservas",
            "bookings": self.service.get_bookings(page,search=search),
            "form": self.form_type(),
            "search_form": self.search_form_type(),
        }
        
        #retorno de plantilla
        return render(request,self.template_name,context)
    
    #metodo post
    def post(self, request:HttpRequest, *args, **kargs):
        #obtener operacion
        operation = request.POST.get("operation")
        
        #obtener datos
        form = self.form_type(request.POST) if operation != "search" else self.search_form_type(request.POST)
        
        #validar formulario
        if form.is_valid():
            #validar operacion
            if operation == "search":
                #obtener valor
                search = form.cleaned_data.get("search")
                #pasar parametro
                return redirect(f"/booking/?search={search}")
            
            #crear reserva
            self.service.create_booking(form.cleaned_data)
            
        #redirigir a vista
        return redirect("/booking/")