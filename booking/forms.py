import django.forms as forms
from .constants import TOURIST_TYPES, BOOOKING_STATES
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

#formulario de eliminacion de reserva
class BookingDropForm(forms.Form):
    #campos del forumario
    id = forms.IntegerField(widget=forms.HiddenInput())
    operation = forms.CharField(initial="drop",widget=forms.HiddenInput())

#formulario de edicion de datos
class BookingModifyForm(forms.Form):
    #campos de informacion de reserva
    id = forms.IntegerField(widget=forms.HiddenInput())
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
    operation = forms.CharField(initial="modify",widget=forms.HiddenInput())
    
#formulario de modificacion de estado
class BookingModifyStatusForm(forms.Form):
    #campos
    id = forms.IntegerField(widget=forms.HiddenInput())
    state = forms.ChoiceField(
        label="Estado",
        choices=enumerate(BOOOKING_STATES),
        required=True,
        widget=forms.Select({
            "class":"inpt-select"
        })
    )
    operation = forms.CharField(initial="modify_status",widget=forms.HiddenInput())