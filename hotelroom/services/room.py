from ..models import HotelRoom
from ..contants import ROOM_STATES

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
        
    def get_rooms(self, start_floor:int, span:int = 4):
        #manejo de error
        try:
            #obtener objetos de forma descendiente
            rooms = HotelRoom.objects.order_by("-floor").filter(floor__gte=start_floor,floor__lte=start_floor+span)
            
            #validacion de vacios
            if not rooms.exists():
                return [[]]
            
            #obtener el piso mas grande
            max_floor = rooms[0].floor
            
            #matriz de habitaciones
            rooms_clustered = [[] for i in range(max_floor)]
            
            #construir matriz y agrupar habitaciones
            index = 0
            for room in rooms:
                #verificar piso
                if room.floor != max_floor:
                    #mover punteros
                    index += (max_floor - room.floor)
                    max_floor = room.floor
                    
                #añadir al piso
                rooms_clustered[index].append({
                    "pk":room.pk, 
                    "floor": room.floor,
                    "type": room.type if room.type else "sin tipo",
                    "state": ROOM_STATES[room.state],
                })
            
            #retornar habitaciones
            return rooms_clustered
        except Exception as e:
            #imprimir mensaje de error
            print(f"Error: {e}")
            
            #retornar fracaso
            return [[]]

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
                
                #validar cambio de estado
                if cleaned_data.get("state"):
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
    