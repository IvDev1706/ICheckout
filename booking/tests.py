from datetime import date

from django.test import TestCase
from hotelroom.models import HotelRoom, RoomType
from .constants import BOOOKING_STATES
from .forms import BookingAddForm
from .models import Booking, BookingRoomAsignment
from .services import BookingService


class BookingServiceTests(TestCase):
    def setUp(self):
        self.service = BookingService()
        self.room_type = RoomType.objects.create(name="Regular", price=850.0)
        self.room = HotelRoom.objects.create(floor=1, type=self.room_type)

    def _create_booking(self, **overrides):
        data = {
            "arrive_date": date(2026, 3, 10),
            "guests": 2,
            "tourist_type": 0,
            "owner": "Juan Perez",
            "rooms": [self.room],
        }
        data.update(overrides)
        return self.service.create_booking(data)

    def test_create_booking_creates_assignment_and_reserves_room(self):
        self.assertTrue(self._create_booking())

        booking = Booking.objects.get()
        self.assertEqual(booking.state, 0)
        self.assertEqual(booking.guests, 2)
        self.assertEqual(booking.tourist_type, 0)
        self.assertEqual(booking.owner, "Juan Perez")
        self.assertEqual(
            BookingRoomAsignment.objects.filter(booking=booking, room=self.room).count(),
            1,
        )

        self.room.refresh_from_db()
        self.assertEqual(self.room.state, 1)

    def test_get_booking_returns_mapped_data(self):
        self._create_booking()
        booking = Booking.objects.get()

        data = self.service.get_booking(booking.pk)

        self.assertEqual(data["pk"], booking.pk)
        self.assertEqual(data["arrive_date"], "10/03/2026")
        self.assertEqual(data["departure_date"], "??/??/????")
        self.assertEqual(data["state"], BOOOKING_STATES[0])
        self.assertEqual(data["tourist_type"], "Nacional")
        self.assertIn(self.room, data["rooms"])

    def test_get_booking_missing_returns_none(self):
        self.assertIsNone(self.service.get_booking(999))

    def test_update_booking_info(self):
        self._create_booking()
        booking = Booking.objects.get()

        self.assertTrue(self.service.update_booking_info({
            "id": booking.pk,
            "arrive_date": date(2026, 4, 1),
            "guests": 3,
            "tourist_type": 1,
            "owner": "Maria Lopez",
        }))

        booking.refresh_from_db()
        self.assertEqual(booking.arrive_date, date(2026, 4, 1))
        self.assertEqual(booking.guests, 3)
        self.assertEqual(booking.tourist_type, 1)
        self.assertEqual(booking.owner, "Maria Lopez")

    def test_update_booking_info_missing_returns_false(self):
        self.assertFalse(self.service.update_booking_info({
            "id": 999,
            "arrive_date": date(2026, 4, 1),
            "guests": 1,
            "tourist_type": 0,
            "owner": "Nadie",
        }))

    def test_status_en_casa_occupies_room(self):
        self._create_booking()
        booking = Booking.objects.get()

        self.assertTrue(self.service.update_booking_status({
            "id": booking.pk,
            "state": "1",
        }))

        booking.refresh_from_db()
        self.room.refresh_from_db()
        self.assertEqual(booking.state, 1)
        self.assertEqual(self.room.state, 2)

    def test_status_terminada_sets_departure_and_frees_room(self):
        self._create_booking()
        booking = Booking.objects.get()

        self.assertTrue(self.service.update_booking_status({
            "id": booking.pk,
            "state": "2",
        }))

        booking.refresh_from_db()
        self.room.refresh_from_db()
        self.assertEqual(booking.state, 2)
        self.assertEqual(booking.departure_date, date.today())
        self.assertEqual(self.room.state, 0)

    def test_status_cancelada_frees_room(self):
        self._create_booking()
        booking = Booking.objects.get()

        self.service.update_booking_status({"id": booking.pk, "state": "1"})
        self.assertTrue(self.service.update_booking_status({
            "id": booking.pk,
            "state": "3",
        }))

        self.room.refresh_from_db()
        self.assertEqual(self.room.state, 0)
        booking.refresh_from_db()
        self.assertIsNone(booking.departure_date)

    def test_delete_booking_removes_assignment(self):
        self._create_booking()
        booking = Booking.objects.get()

        self.assertTrue(self.service.delete_booking(booking.pk))

        self.assertFalse(Booking.objects.filter(pk=booking.pk).exists())
        self.assertFalse(BookingRoomAsignment.objects.exists())

    def test_delete_missing_booking_returns_false(self):
        self.assertFalse(self.service.delete_booking(999))

    def test_get_bookings_search_by_owner(self):
        self._create_booking(owner="Carlos Ramirez")
        self._create_booking(owner="Ana Torres")

        results = self.service.get_bookings(1, search="Carlos")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["owner"], "Carlos Ramirez")

    def test_get_bookings_search_by_arrive_date(self):
        self._create_booking(arrive_date=date(2026, 5, 20))
        self._create_booking(arrive_date=date(2026, 6, 15))

        results = self.service.get_bookings(1, search="20/05/2026")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["arrive_date"], "20/05/2026")

    def test_get_bookings_without_results_returns_empty_list(self):
        self.assertEqual(self.service.get_bookings(1, search="nadie"), [])


class BookingAddFormTests(TestCase):
    def setUp(self):
        self.room_type = RoomType.objects.create(name="Regular", price=850.0)

    def _rooms(self):
        # el campo de cada formulario debe consultar la base en ese momento
        return list(BookingAddForm().fields["rooms"].queryset)

    def test_rooms_queryset_is_evaluated_per_form(self):
        first_room = HotelRoom.objects.create(floor=1, type=self.room_type)
        self.assertIn(first_room, self._rooms())

        # una habitacion creada despues debe aparecer en el siguiente formulario
        second_room = HotelRoom.objects.create(floor=1, type=self.room_type)
        self.assertIn(second_room, self._rooms())

        # y una habitacion ocupada debe desaparecer del siguiente formulario
        second_room.state = 1
        second_room.save()
        self.assertNotIn(second_room, self._rooms())


class BookingViewTests(TestCase):
    def setUp(self):
        session = self.client.session
        session["user_id"] = 1
        session["user_role"] = "recepcionista"
        session.save()

        self.room_type = RoomType.objects.create(name="VIP", price=1600.0)
        self.room = HotelRoom.objects.create(floor=1, type=self.room_type)

    def _booking(self, **overrides):
        data = {
            "arrive_date": date(2026, 3, 10),
            "guests": 2,
            "state": 0,
            "tourist_type": 1,
            "owner": "Laura Gomez",
        }
        data.update(overrides)
        booking = Booking.objects.create(**data)
        BookingRoomAsignment.objects.create(booking=booking, room=self.room)
        return booking

    def test_index_renders(self):
        response = self.client.get("/booking/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("bookings", response.context)

    def test_index_creates_booking(self):
        response = self.client.post("/booking/", {
            "arrive_date": "10/03/2026",
            "guests": "2",
            "tourist_type": "0",
            "owner": "Juan Perez",
            "rooms": [str(self.room.pk)],
        })

        self.assertRedirects(response, "/booking/", fetch_redirect_response=False)
        self.assertEqual(Booking.objects.count(), 1)
        self.room.refresh_from_db()
        self.assertEqual(self.room.state, 1)

    def test_index_search_redirects_with_query(self):
        response = self.client.post("/booking/", {
            "operation": "search",
            "search": "Laura",
        })

        self.assertRedirects(
            response, "/booking/?search=Laura", fetch_redirect_response=False
        )

    def test_detail_renders(self):
        booking = self._booking()

        response = self.client.get(f"/booking/{booking.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["booking"]["pk"], booking.pk)

    def test_modify_booking(self):
        booking = self._booking()

        response = self.client.post(f"/booking/{booking.pk}/", {
            "operation": "modify",
            "id": str(booking.pk),
            "arrive_date": "01/04/2026",
            "guests": "4",
            "tourist_type": "0",
            "owner": "Pedro Sanchez",
        })

        self.assertRedirects(
            response, f"/booking/{booking.pk}", fetch_redirect_response=False
        )
        booking.refresh_from_db()
        self.assertEqual(booking.arrive_date, date(2026, 4, 1))
        self.assertEqual(booking.guests, 4)
        self.assertEqual(booking.owner, "Pedro Sanchez")

    def test_modify_status(self):
        booking = self._booking()

        self.client.post(f"/booking/{booking.pk}/", {
            "operation": "modify_status",
            "id": str(booking.pk),
            "state": "1",
        })

        booking.refresh_from_db()
        self.room.refresh_from_db()
        self.assertEqual(booking.state, 1)
        self.assertEqual(self.room.state, 2)

    def test_drop_booking(self):
        booking = self._booking()

        response = self.client.post(f"/booking/{booking.pk}/", {
            "operation": "drop",
            "id": str(booking.pk),
        })

        self.assertRedirects(
            response, f"/booking/{booking.pk}", fetch_redirect_response=False
        )
        self.assertFalse(Booking.objects.filter(pk=booking.pk).exists())
