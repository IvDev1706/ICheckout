
from django.core.exceptions import ObjectDoesNotExist
from .constants import BOOOKING_STATES, TOURIST_TYPES
from .models import Booking, BookingRoomAsignment, HotelRoom

#clase de servicio de reservas
class BookingService:
    #operaciones
    def get_bookings(self, page:int, per_page:int = 10):
        #manejo de error
        try:
            #obtener datos
            bookings = Booking.objects.filter(id__gte=page+1,id__lte=(page+1)*per_page)
            
            #si no hay nada
            if not bookings.exists():
                return [] #lista vacia
            
            #retornar datos
            return [{
                "pk": booking.pk,
                "arrive_date": booking.arrive_date.strftime("%d/%m/%Y"),
                "departure_date": booking.departure_date.strftime("%d/%m/%Y") if booking.departure_date else "??/??/????",
                "guests": booking.guests,
                "state": BOOOKING_STATES[booking.state],
                "tourist_type": TOURIST_TYPES[booking.tourist_type],
                "owner": booking.owner
            } for booking in bookings]
        except Exception as e:
            #imprimir mensaje
            print(f"Error: {e}")
            #retornar vacio
            return []
    
    def get_booking(self, id:int):
            #manejo de error
            try:
                #obtener datos
                booking = Booking.objects.get(id=id)
                
                #obtener ids de habitacion
                room_ids = BookingRoomAsignment.objects.filter(booking=booking).values_list('room',flat=True)
                rooms = HotelRoom.objects.filter(pk__in=room_ids)
                
                #retornar datos
                return {
                    "pk": booking.pk,
                    "arrive_date": booking.arrive_date.strftime("%d/%m/%Y"),
                    "departure_date": booking.departure_date.strftime("%d/%m/%Y") if booking.departure_date else "??/??/????",
                    "guests": booking.guests,
                    "state": BOOOKING_STATES[booking.state],
                    "tourist_type": TOURIST_TYPES[booking.tourist_type],
                    "owner": booking.owner,
                    "rooms": rooms
                }
            except ObjectDoesNotExist as e:
                #imprimir mensaje
                print(f"Error: {e}")
                #retornar vacio
                return []
            
    def create_booking(self, cleaned_data:dict):
        #manejo de error
        try:
            #crear la reserva
            booking = Booking.objects.create(
                arrive_date=cleaned_data.get("arrive_date"),
                guests=cleaned_data.get("guests"),
                tourist_type=cleaned_data.get("tourist_type"),
                owner=cleaned_data.get("owner")
            )
            
            #crear asignaciones
            for room in cleaned_data.get("rooms"):
                #crear entrada en asignacion
                BookingRoomAsignment.objects.create(
                    booking=booking,
                    room=room
                )
                
            #retornar exito
            return True
        except Exception as e:
            #mensaje de error
            print(f"Error: {e}")
            #retornar falso
            return False
            