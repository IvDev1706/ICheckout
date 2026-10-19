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
    model = forms.CharField(initial='hotelroom',widget=forms.HiddenInput())
    operation = forms.CharField(initial="modify",widget=forms.HiddenInput())