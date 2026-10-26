import django.forms as forms
from .constants import TOURIST_TYPES
from .models import HotelRoom

#formulario de registro
class BookingAddForm(forms.Form):
    #campos del formulario
    arrive_date = forms.DateField(
        label="Fecha de llegada",
        required=True,
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput({
            "class": "inpt",
            "placeholder": "DD/MM/YYYY"
        },format='%d/%m/%Y')
    )
    guests = forms.IntegerField(
        label="Numero de huespedes",
        required=True,
        widget=forms.NumberInput({
            "class": "inpt",
            "placeholder": 2
        })
    )
    tourist_type = forms.ChoiceField(
        label="Tipo de turista",
        choices=enumerate(TOURIST_TYPES),
        required=True,
        widget=forms.Select({
            "class":"inpt-select"
        })
    )
    owner = forms.CharField(
        label="Titular de la reserva",
        max_length=30,
        required=True,
        widget=forms.TextInput({
            "class": "inpt"
        })
    )
    rooms = forms.ModelMultipleChoiceField(
        label="Habitaciones disponibles",
        queryset=HotelRoom.objects.filter(state=0),
        required=True,
        widget=forms.SelectMultiple({
            "class":"inpt-select"
        })
    )