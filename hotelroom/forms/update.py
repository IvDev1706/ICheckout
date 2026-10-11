import django.forms as forms
from ..models import RoomType

#estados de habitacion
STATE_CHOICES = [
    (0,'Disponible'),
    (1,'Reservada'),
    (2,'Ocupada')
]

#formulario de actualizacion de habitacion
class HotelRoomModifyForm(forms.Form):
    #campos del formulario
    id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    floor = forms.IntegerField(
        label="Piso:",
        required=True,
        widget=forms.TextInput({
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
    state = forms.ChoiceField(
        label="Estado",
        choices=STATE_CHOICES,
        required=True,
        widget=forms.Select({
            "class": "inpt-select"
        })
    )
    model = forms.CharField(initial='hotelroom',widget=forms.HiddenInput())