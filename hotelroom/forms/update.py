import django.forms as forms
from ..models import RoomType
from ..contants import STATE_CHOICES

#formulario de actualizacion de habitacion
class HotelRoomModifyForm(forms.Form):
    #campos del formulario
    id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    floor = forms.IntegerField(
        label="Piso:",
        required=True,
        widget=forms.NumberInput({
            "class":"inpt"
        })
    )
    type = forms.ModelChoiceField(
        label="Tipo de habitacion",
        queryset=RoomType.objects.all(),
        empty_label="selecciona tipo de habitacion",
        required=True,
        widget=forms.Select({
            "class": "inpt-select"
        })
    )
    operation = forms.CharField(initial="modify",widget=forms.HiddenInput())
    
class RoomTypeModifyForm(forms.Form):
    #campos del formulario
    id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    name = forms.CharField(
        label="Nombre",
        required=True,
        widget=forms.TextInput({
            "class":"inpt"
        })
    )
    price = forms.FloatField(
        label="Precio por noche",
        required=True,
        widget=forms.NumberInput({
            "class": "inpt",
            "min": 0
        })
    )
    operation = forms.CharField(initial="modify",widget=forms.HiddenInput())