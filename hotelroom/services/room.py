from ..models import HotelRoom

#servicio para habitaciones
class HotelRoomService:
    #operaciones
    def get_room(self,id:int):
        #manejo de error
        try:
            #obtener objeto
            return HotelRoom.objects.get(id=id)
        except Exception as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            
            #retornar fracaso
            return None
        
    def get_rooms(self):
        #manejo de error
        try:
            #obtener objetos de forma descendiente
            return HotelRoom.objects.order_by("-floor").all()
        except Exception as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            
            #retornar fracaso
            return None

    def create_room(self,cleaned_data:dict):
        #manejo de error
        try:
            #crear nueva habitacion
            HotelRoom.objects.create(
                floor=cleaned_data.get("floor"),
                type=cleaned_data.get("type")
            )
            
            #retornar exito
            return True
        except Exception as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            
            #retornar fracaso
            return False
        
    def update_room(self,cleaned_data:dict):
            #manejo de error
            try:
                #crear nueva habitacion
                room = HotelRoom.objects.get(id=cleaned_data.get("id"))
                
                #actualizar datos
                room.floor = cleaned_data.get("floor")
                room.type = cleaned_data.get("type")
                room.state = cleaned_data.get("state")
                
                #guardar en bd
                room.save()
                
                #retornar exito
                return True
            except Exception as e:
                #imprimir mensaje de error
                print(f"Error: {e}")
                
                #retornar fracaso
                return False
        
    def delete_room(self,id:int):
        #manejo de error
        try:
            #buscar objeto
            room = HotelRoom.objects.get(id=id)
            
            #eliminar de la base de datos
            room.delete()
            
            #exito
            return True
        except Exception as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            
            #retornar fracaso
            return False
    