import bcrypt
from django.core.exceptions import ObjectDoesNotExist
from .models import ICUser

#servicio para usuario
class UserService:
    #operaciones
    def get_user(self, id:int):
        #manejo de error
        try:
            #retornar usuario
            return ICUser.objects.get(id=id)
        except ObjectDoesNotExist as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            #retornar falso
            return None
    
    def validate_user(self, cleaned_data:dict):
        #manejo de error
        try:
            #validar credenciales
            u = ICUser.objects.get(
                name=cleaned_data.get("name")
            )
            
            #validar contraseña
            raw_password = cleaned_data.get("password")
            valid = bcrypt.checkpw(raw_password.encode(),u.password.encode())
            
            #retornar id
            return u.pk if valid else 0
        except ObjectDoesNotExist as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            #retornar falso
            return 0
        
    def create_user(self, cleaned_data:dict):
        #manejo de error
        try:
            #obtener contraseña cruda
            raw_password = cleaned_data.get("password").encode()
            
            #hashear contraseña
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(raw_password,salt)
            
            #crear usuario en bd
            ICUser.objects.create(
                name=cleaned_data.get("name"),
                password=hashed_password.decode(),
                role=cleaned_data.get("role")
            )
            
            #retornar exito
            return True
        except Exception as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            #retornar fracaso
            return False