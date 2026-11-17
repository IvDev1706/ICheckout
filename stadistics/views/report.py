import csv
from io import StringIO
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views import View
from ..constants import MONTHS
from ..forms import StatisticsFilterForm
from ..services import StatisticsService

#vista de exportacion de reservas en csv
class ReportView(View):
    #atributos
    service = StatisticsService()
    filter_form_class = StatisticsFilterForm
    
    #metodo get
    def get(self, request:HttpRequest, *args, **kargs):
        #validar periodo recibido
        form = self.filter_form_class(
            request.GET or None,
            years=self.service.get_years()
        )
        if not form.is_valid():
            return HttpResponseBadRequest("Periodo invalido")
        
        #obtener periodo seleccionado
        month = int(form.cleaned_data.get("month"))
        year = int(form.cleaned_data.get("year"))
        
        #crear archivo csv
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Reserva",
            "Fecha de llegada",
            "Fecha de salida",
            "Huéspedes",
            "Estado",
            "Tipo de turista",
            "Titular",
            "Habitaciones",
        ])
        
        #agregar una fila por reserva
        for booking in self.service.get_bookings_report(month, year):
            writer.writerow([
                f"R-{booking['pk']}",
                booking["arrive_date"],
                booking["departure_date"],
                booking["guests"],
                booking["state"],
                booking["tourist_type"],
                booking["owner"],
                booking["rooms"],
            ])
        
        #preparar descarga (utf-8 con bom para conservar acentos en excel)
        response = HttpResponse(
            output.getvalue().encode("utf-8-sig"),
            content_type="text/csv; charset=utf-8"
        )
        filename = f"reservas_{MONTHS[month - 1].lower()}_{year}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
