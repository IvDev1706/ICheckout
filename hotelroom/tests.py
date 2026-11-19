from django.db import transaction
from django.test import TestCase
from .models import HotelRoom, RoomType
from .services import HotelRoomService, RoomTypeService


class RoomTypeServiceTests(TestCase):
    def setUp(self):
        self.service = RoomTypeService()

    def test_create_type(self):
        self.assertTrue(self.service.create_type({"name": "Suite", "price": 3200.0}))

        room_type = RoomType.objects.get(name="Suite")
        self.assertEqual(room_type.price, 3200.0)

    def test_create_duplicated_name_fails(self):
        self.service.create_type({"name": "VIP", "price": 1600.0})

        # el servicio atrapa el IntegrityError; el savepoint evita romper la transaccion
        with transaction.atomic():
            self.assertFalse(self.service.create_type({"name": "VIP", "price": 1700.0}))
        self.assertEqual(RoomType.objects.filter(name="VIP").count(), 1)

    def test_get_types_and_get_type(self):
        self.service.create_type({"name": "Regular", "price": 850.0})
        self.service.create_type({"name": "VIP", "price": 1600.0})

        self.assertEqual(self.service.get_types().count(), 2)
        room_type = RoomType.objects.get(name="VIP")
        self.assertEqual(self.service.get_type(room_type.pk), room_type)

    def test_get_type_missing_returns_none(self):
        self.assertIsNone(self.service.get_type(999))

    def test_update_type(self):
        self.service.create_type({"name": "VIP", "price": 1600.0})
        room_type = RoomType.objects.get(name="VIP")

        self.assertTrue(self.service.update_type({
            "id": room_type.pk,
            "name": "VIP Plus",
            "price": 1800.0,
        }))

        room_type.refresh_from_db()
        self.assertEqual(room_type.name, "VIP Plus")
        self.assertEqual(room_type.price, 1800.0)

    def test_delete_type_sets_rooms_type_to_null(self):
        self.service.create_type({"name": "Suite", "price": 3200.0})
        room_type = RoomType.objects.get(name="Suite")
        room = HotelRoom.objects.create(floor=1, type=room_type)

        self.assertTrue(self.service.delete_type(room_type.pk))

        self.assertFalse(RoomType.objects.filter(pk=room_type.pk).exists())
        room.refresh_from_db()
        self.assertIsNone(room.type)

    def test_delete_missing_type_returns_false(self):
        self.assertFalse(self.service.delete_type(999))


class HotelRoomServiceTests(TestCase):
    def setUp(self):
        self.service = HotelRoomService()
        self.room_type = RoomType.objects.create(name="Regular", price=850.0)
        self.suite = RoomType.objects.create(name="Suite", price=3200.0)

    def test_create_room(self):
        self.assertTrue(self.service.create_room({
            "floor": 2,
            "type": self.room_type,
        }))

        room = HotelRoom.objects.get()
        self.assertEqual(room.floor, 2)
        self.assertEqual(room.state, 0)
        self.assertEqual(room.type, self.room_type)

    def test_get_room_missing_returns_none(self):
        self.assertIsNone(self.service.get_room(999))

    def test_update_room_changes_floor_type_and_state(self):
        room = HotelRoom.objects.create(floor=1, type=self.room_type)

        self.assertTrue(self.service.update_room({
            "id": room.pk,
            "floor": 4,
            "type": self.suite,
            "state": 2,
        }))

        room.refresh_from_db()
        self.assertEqual(room.floor, 4)
        self.assertEqual(room.type, self.suite)
        self.assertEqual(room.state, 2)

    def test_delete_room(self):
        room = HotelRoom.objects.create(floor=1, type=self.room_type)

        self.assertTrue(self.service.delete_room(room.pk))
        self.assertFalse(HotelRoom.objects.filter(pk=room.pk).exists())

    def test_delete_missing_room_returns_false(self):
        self.assertFalse(self.service.delete_room(999))

    def test_get_rooms_groups_by_floor_descending(self):
        HotelRoom.objects.create(floor=1, type=self.room_type)
        HotelRoom.objects.create(floor=1, type=self.suite)
        HotelRoom.objects.create(floor=2, type=self.room_type)

        clusters = self.service.get_rooms(1, 2)

        self.assertEqual(len(clusters), 2)
        self.assertEqual(len(clusters[0]), 1)  # piso 2
        self.assertEqual(len(clusters[1]), 2)  # piso 1
        self.assertEqual(clusters[1][0]["floor"], 1)
        self.assertEqual(clusters[1][0]["state"], "Disponible")

    def test_get_rooms_without_data_returns_empty_matrix(self):
        self.assertEqual(self.service.get_rooms(1, 2), [[]])


class HotelRoomViewTests(TestCase):
    def setUp(self):
        session = self.client.session
        session["user_id"] = 1
        session["user_role"] = "recepcionista"
        session.save()
        self.room_type = RoomType.objects.create(name="Regular", price=850.0)

    def test_index_renders(self):
        HotelRoom.objects.create(floor=1, type=self.room_type)

        response = self.client.get("/room/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("rooms", response.context)

    def test_index_creates_room_type(self):
        self.client.post("/room/", {
            "model": "roomtype",
            "name": "Suite",
            "price": "3200",
        })

        self.assertTrue(RoomType.objects.filter(name="Suite").exists())

    def test_index_creates_room(self):
        self.client.post("/room/", {
            "model": "hotelroom",
            "floor": "3",
            "type": str(self.room_type.pk),
        })

        self.assertTrue(HotelRoom.objects.filter(floor=3).exists())

    def test_index_pagination_redirects_with_filters(self):
        response = self.client.post("/room/", {
            "model": "hotelroom__pagination",
            "start_floor": "2",
            "span": "3",
        })

        self.assertRedirects(
            response,
            "/room/?start_floor=2&span=3",
            fetch_redirect_response=False,
        )

    def test_room_detail_renders(self):
        room = HotelRoom.objects.create(floor=1, type=self.room_type)

        response = self.client.get(f"/room/{room.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["room"]["pk"], room.pk)

    def test_room_modify(self):
        suite = RoomType.objects.create(name="Suite", price=3200.0)
        room = HotelRoom.objects.create(floor=1, type=self.room_type)

        response = self.client.post(f"/room/{room.pk}/", {
            "operation": "modify",
            "id": str(room.pk),
            "floor": "4",
            "type": str(suite.pk),
        })

        self.assertRedirects(
            response, f"/room/{room.pk}", fetch_redirect_response=False
        )
        room.refresh_from_db()
        self.assertEqual(room.floor, 4)
        self.assertEqual(room.type, suite)

    def test_room_drop(self):
        room = HotelRoom.objects.create(floor=1, type=self.room_type)

        response = self.client.post(f"/room/{room.pk}/", {
            "operation": "drop",
            "id": str(room.pk),
        })

        self.assertRedirects(response, "/room/", fetch_redirect_response=False)
        self.assertFalse(HotelRoom.objects.filter(pk=room.pk).exists())

    def test_type_modify(self):
        response = self.client.post(f"/room/type/{self.room_type.pk}/", {
            "operation": "modify",
            "id": str(self.room_type.pk),
            "name": "Regular Plus",
            "price": "900",
        })

        self.assertRedirects(
            response,
            f"/room/type/{self.room_type.pk}",
            fetch_redirect_response=False,
        )
        self.room_type.refresh_from_db()
        self.assertEqual(self.room_type.name, "Regular Plus")

    def test_type_drop(self):
        room_type = RoomType.objects.create(name="Temp", price=100.0)

        response = self.client.post(f"/room/type/{room_type.pk}/", {
            "operation": "drop",
            "id": str(room_type.pk),
        })

        self.assertRedirects(response, "/room/", fetch_redirect_response=False)
        self.assertFalse(RoomType.objects.filter(pk=room_type.pk).exists())
