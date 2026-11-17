from datetime import date
from django.views import View
from django.http import HttpRequest
from django.shortcuts import render
from ..constants import MONTHS
from ..forms import StatisticsFilterForm
from ..services import StatisticsService

#vista principal de estadisticas
class IndexView(View):
    #atributos
    template_name = "stadistics.html"
    service = StatisticsService()
    filter_form_class = StatisticsFilterForm
    
    #metodo get
    def get(self, request:HttpRequest, *args, **kargs):
        #periodo por defecto (mes y año actuales)
        today = date.today()
        month = today.month
        year = today.year
        
        #obtener años disponibles
        years = self.service.get_years()
        
        #validar filtro recibido
        form = self.filter_form_class(request.GET or None, years=years)
        if form.is_valid():
            #usar periodo seleccionado
            month = int(form.cleaned_data.get("month"))
            year = int(form.cleaned_data.get("year"))
        else:
            #mostrar el periodo actual en el formulario
            form = self.filter_form_class(initial={
                "month": month,
                "year": year
            }, years=years)
        
        #preparar contexto
        context = {
            "title": "ICheckout - Estadísticas",
            "subtitle": "ICheckout - Estadísticas",
            "form": form,
            "period": f"{MONTHS[month - 1]} {year}",
            "chart_data": self.service.get_report(month, year),
        }
        
        #retorno de plantilla
        return render(request, self.template_name, context)
