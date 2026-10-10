from ..models import RoomType

#servicio para tipos de habitacion
class RoomTypeService:
    #operaciones
    def get_types(self):
        #manejo de error
        try:
            #obtener objetos
            return RoomType.objects.all()
        except Exception as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            
            #retornar fracaso
            return None
        
    def get_type(self, id:int):
        #manejo de error
        try:
            #obtener objeto
            return RoomType.objects.get(id=id)
        except Exception as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            
            #retornar fracaso
            return None
        
    def create_type(self, cleaned_data:dict):
        #manejo de error
        try:
            #crear objeto
            RoomType.objects.create(
                name=cleaned_data.get("name"),
                price=RoomType.objects.get("price")
            )
            
            #retornar exito
            return True
        except Exception as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            
            #retornar fracaso
            return False
        
    def delete_type(self, id:int):
        #manejo de error
        try:
            #buscar el objeto
            type = RoomType.objects.get(id=id)
            
            #eliminar el objeto
            type.delete()
            
            #retornar exito
            return True
        except Exception as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            
            #retornar fracaso
            return False