import django.forms as forms
from .constants import USER_ROLES

#formulario de login
class LoginForm(forms.Form):
    #campos de login
    name = forms.CharField(
        label='Usuario:',
        max_length=15,
        required=True,
        widget=forms.TextInput({
            "class": "inpt"
        })
    )
    password = forms.CharField(
        label='Contraseña:',
        max_length=10,
        required=True,
        widget=forms.PasswordInput({
            "class": "inpt"
        })
    )
    
#formulario de signup
class SignUpForm(forms.Form):
    #campos de login
    name = forms.CharField(
        label='Usuario:',
        max_length=15,
        required=True,
        widget=forms.TextInput({
            "class": "inpt"
        })
    )
    password = forms.CharField(
        label='Contraseña:',
        max_length=10,
        required=True,
        widget=forms.PasswordInput({
            "class": "inpt"
        })
    )
    role = forms.ChoiceField(
        label='Rol',
        choices=[
            ('','-- seleccione un rol --'),
            (USER_ROLES[0],USER_ROLES[0].capitalize()),
            (USER_ROLES[1],USER_ROLES[1].capitalize())
        ],
        required=True,
        widget=forms.Select({
            "class":"inpt-select"
        })
    )