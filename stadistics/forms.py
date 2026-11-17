import django.forms as forms
from datetime import date
from .constants import MONTHS

#formulario de filtro por mes y año
class StatisticsFilterForm(forms.Form):
    #campos del formulario
    month = forms.ChoiceField(
        label="Mes",
        choices=[(index + 1, name) for index, name in enumerate(MONTHS)],
        required=True,
        widget=forms.Select({
            "class": "inpt-select"
        })
    )
    year = forms.ChoiceField(
        label="Año",
        required=True,
        widget=forms.Select({
            "class": "inpt-select"
        })
    )
    
    #inyectar los años disponibles
    def __init__(self, *args, years:list=None, **kargs):
        super().__init__(*args, **kargs)
        #usar el año actual si no se reciben opciones
        years = years or [date.today().year]
        self.fields["year"].choices = [(year, year) for year in years]
