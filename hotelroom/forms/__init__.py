import django.forms as forms
from .create import HotelRoomAddForm, RoomTypeAddForm
from .delete import HotelRoomDropForm, RoomTypeDropForm
from .update import HotelRoomModifyForm, RoomTypeModifyForm

#formulario para paginado de habitaciones
class HotelRoomPaginationForm(forms.Form):
    #campos del formulario
    start_floor = forms.IntegerField(
        label="Piso inicial",
        min_value=1,
        required=True,
        widget=forms.NumberInput({
            "class": "inpt",
            "placeholder": "piso inicial"
        })
    )
    span = forms.IntegerField(
        label="Expandir",
        min_value=1,
        max_value=10,
        widget=forms.NumberInput({
            "class":"inpt",
            "placeholder": "pisos a expandir"
        })
    )
    model = forms.CharField(
        initial="hotelroom__pagination",
        widget=forms.HiddenInput()
    )