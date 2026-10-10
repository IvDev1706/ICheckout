import django.forms as forms

#formulario de baja de tipo de habitacion
class RoomTypeDropForm(forms.Form):
    #campo pre-llenado
    id = forms.IntegerField(widget=forms.HiddenInput())
    operation = forms.CharField(initial="drop",widget=forms.HiddenInput())

#formulario de baja de habitacion
class HotelRoomDropForm(forms.Form):
    #campo pre-llenado
    id = forms.IntegerField(widget=forms.HiddenInput())
    operation = forms.CharField(initial="drop",widget=forms.HiddenInput())