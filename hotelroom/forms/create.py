import django.forms as forms
from ..models import RoomType

#formulario de registro de tipo de habitacion
class RoomTypeAddForm(forms.Form):
    #campos del formulario
    name = forms.CharField(
        label="Nombre:",
        max_length=15,
        required=True,
        widget=forms.TextInput({
            "placeholder":"regular/vip/suite/etc...",
            "class":"inpt"
        })
    )
    price = forms.FloatField(
            label="Precio por noche:",
            required=True,
            widget=forms.NumberInput({
                "placeholder":"1000",
                "class":"inpt",
                "min": 0
            })
        )
    model = forms.CharField(initial='roomtype',widget=forms.HiddenInput())
    

#formulario de registro de habitacion
class HotelRoomAddForm(forms.Form):
    #campos del formulario
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
        widget=forms.Select({
            "class": "inpt-select"
        })
    )
    model = forms.CharField(initial='hotelroom',widget=forms.HiddenInput())