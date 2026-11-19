from datetime import date

from django.test import TestCase
from booking.models import Booking, BookingRoomAsignment
from hotelroom.models import HotelRoom, RoomType
from .constants import MONTHS
from .services import StatisticsService


class StatisticsServiceTests(TestCase):
    def setUp(self):
        self.service = StatisticsService()
        self.year = date.today().year
        self.regular = RoomType.objects.create(name="Regular", price=850.0)
        self.vip = RoomType.objects.create(name="VIP", price=1600.0)

    def _booking(self, arrive, owner="Juan Perez", tourist_type=0, state=2, room_type=None):
        booking = Booking.objects.create(
            arrive_date=arrive,
            departure_date=arrive,
            guests=2,
            state=state,
            tourist_type=tourist_type,
            owner=owner,
        )
        room = HotelRoom.objects.create(
            floor=1, type=room_type or self.regular, state=0
        )
        BookingRoomAsignment.objects.create(booking=booking, room=room)
        return booking

    def test_get_years_includes_current_and_booking_years(self):
        self._booking(date(self.year - 1, 5, 10))

        years = self.service.get_years()

        self.assertIn(self.year, years)
        self.assertIn(self.year - 1, years)
        self.assertEqual(years, sorted(years, reverse=True))

    def test_get_years_without_bookings_returns_current_year(self):
        self.assertEqual(self.service.get_years(), [date.today().year])

    def test_get_report_tourist_types(self):
        self._booking(date(self.year, 3, 10), tourist_type=0)
        self._booking(date(self.year, 3, 11), tourist_type=1)

        report = self.service.get_report(3, self.year)

        self.assertEqual(report["tourist_types"]["labels"], ["Nacional", "Extranjero"])
        self.assertEqual(report["tourist_types"]["values"], [1, 1])

    def test_get_report_room_types(self):
        self._booking(date(self.year, 3, 10), room_type=self.vip)
        self._booking(date(self.year, 3, 12), room_type=self.vip)
        self._booking(date(self.year, 3, 14), room_type=self.regular)

        report = self.service.get_report(3, self.year)

        self.assertEqual(report["room_types"]["labels"][0], "VIP")
        self.assertEqual(report["room_types"]["values"], [2, 1])

    def test_get_report_bookings_per_day_has_all_days(self):
        self._booking(date(self.year, 2, 5))

        report = self.service.get_report(2, self.year)

        values = report["bookings_per_day"]["values"]
        self.assertEqual(len(values), 28)
        self.assertEqual(values[4], 1)  # dia 5

    def test_get_report_booking_states(self):
        self._booking(date(self.year, 4, 1), state=3)
        self._booking(date(self.year, 4, 2), state=2)
        self._booking(date(self.year, 4, 3), state=0)

        report = self.service.get_report(4, self.year)

        self.assertEqual(report["booking_states"]["labels"], ["Cancelada", "Terminada"])
        self.assertEqual(report["booking_states"]["values"], [1, 1])

    def test_get_report_empty_period(self):
        report = self.service.get_report(1, self.year)

        self.assertEqual(
            report["tourist_types"], {"labels": ["Nacional", "Extranjero"], "values": [0, 0]}
        )
        self.assertEqual(report["room_types"], {"labels": [], "values": []})
        self.assertEqual(report["booking_states"]["values"], [0, 0])

    def test_get_bookings_report_lists_rooms(self):
        self._booking(date(self.year, 7, 9), owner="Lucia Ortega")

        rows = self.service.get_bookings_report(7, self.year)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["owner"], "Lucia Ortega")
        self.assertEqual(rows[0]["arrive_date"], "09/07/%d" % self.year)
        self.assertTrue(rows[0]["rooms"].startswith("H-"))

    def test_get_bookings_report_ignores_other_months(self):
        self._booking(date(self.year, 7, 9))

        self.assertEqual(self.service.get_bookings_report(8, self.year), [])


class StadisticsViewTests(TestCase):
    def setUp(self):
        session = self.client.session
        session["user_id"] = 1
        session["user_role"] = "Analista"
        session.save()

        self.year = date.today().year
        room_type = RoomType.objects.create(name="Suite", price=3200.0)
        room = HotelRoom.objects.create(floor=1, type=room_type)
        booking = Booking.objects.create(
            arrive_date=date(self.year, 3, 8),
            departure_date=date(self.year, 3, 9),
            guests=2,
            state=2,
            tourist_type=0,
            owner="Silvia Serrano",
        )
        BookingRoomAsignment.objects.create(booking=booking, room=room)

    def test_index_renders_current_period(self):
        response = self.client.get("/stadistics/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("chart_data", response.context)
        self.assertEqual(response.context["period"], f"{MONTHS[date.today().month - 1]} {self.year}")

    def test_index_uses_filter_period(self):
        response = self.client.get(f"/stadistics/?month=3&year={self.year}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["period"], f"Marzo {self.year}")

    def test_index_redirects_without_session(self):
        self.client.session.flush()

        response = self.client.get("/stadistics/")

        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_report_downloads_csv(self):
        response = self.client.get(f"/stadistics/report/?month=3&year={self.year}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn(
            f'reservas_marzo_{self.year}.csv', response["Content-Disposition"]
        )

        content = response.content.decode("utf-8-sig")
        self.assertIn("Titular", content)
        self.assertIn("Silvia Serrano", content)

    def test_report_rejects_invalid_period(self):
        response = self.client.get("/stadistics/report/")

        self.assertEqual(response.status_code, 400)
