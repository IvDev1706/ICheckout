import bcrypt
from django.db import transaction
from django.test import TestCase
from .forms import LoginForm, SignUpForm
from .models import ICUser
from .services import UserService

class UserServiceTests(TestCase):
    def setUp(self):
        self.service = UserService()

    def test_create_user_hashes_password(self):
        result = self.service.create_user({
            "name": "recepcion",
            "password": "Recepcion123!",
            "role": "recepcionista",
        })

        self.assertTrue(result)
        user = ICUser.objects.get(name="recepcion")
        self.assertNotEqual(user.password, "Recepcion123!")
        self.assertEqual(user.role, "recepcionista")
        self.assertTrue(bcrypt.checkpw(b"Recepcion123!", user.password.encode()))

    def test_create_user_rejects_duplicate_name(self):
        data = {"name": "analista", "password": "Analista123!", "role": "Analista"}
        self.assertTrue(self.service.create_user(data))
        # el servicio atrapa el IntegrityError; el savepoint evita romper la transaccion
        with transaction.atomic():
            self.assertFalse(self.service.create_user(data))
        self.assertEqual(ICUser.objects.filter(name="analista").count(), 1)

    def test_validate_user_returns_id_with_correct_password(self):
        self.service.create_user({
            "name": "recepcion",
            "password": "Recepcion123!",
            "role": "recepcionista",
        })

        user_id = self.service.validate_user({
            "name": "recepcion",
            "password": "Recepcion123!",
        })

        self.assertEqual(user_id, ICUser.objects.get(name="recepcion").pk)

    def test_validate_user_returns_zero_with_wrong_password(self):
        self.service.create_user({
            "name": "recepcion",
            "password": "Recepcion123!",
            "role": "recepcionista",
        })

        self.assertEqual(
            self.service.validate_user({"name": "recepcion", "password": "incorrecta"}),
            0,
        )

    def test_validate_user_returns_zero_with_unknown_user(self):
        self.assertEqual(
            self.service.validate_user({"name": "nadie", "password": "x"}),
            0,
        )

    def test_get_user_missing_returns_none(self):
        self.assertIsNone(self.service.get_user(999))


class LoginFormTests(TestCase):
    def test_accepts_password_longer_than_ten_characters(self):
        form = LoginForm({"name": "recepcion", "password": "Recepcion123!"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_empty_fields(self):
        form = LoginForm({"name": "", "password": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("password", form.errors)


class LoginFlowTests(TestCase):
    def setUp(self):
        UserService().create_user({
            "name": "recepcion",
            "password": "Recepcion123!",
            "role": "recepcionista",
        })
        UserService().create_user({
            "name": "analista",
            "password": "Analista123!",
            "role": "Analista",
        })
        self.user = ICUser.objects.get(name="recepcion")

    def test_get_login_clears_session(self):
        session = self.client.session
        session["user_id"] = 99
        session.save()

        self.client.get("/")

        self.assertNotIn("user_id", self.client.session)

    def test_post_valid_credentials_creates_session_and_cookie(self):
        response = self.client.post(
            "/",
            {"name": "recepcion", "password": "Recepcion123!"},
        )

        self.assertRedirects(response, "/home/", fetch_redirect_response=False)
        self.assertIn("sessionid", response.cookies)
        self.assertEqual(self.client.session["user_id"], self.user.pk)
        self.assertEqual(self.client.session["user_role"], "recepcionista")

    def test_post_wrong_password_does_not_create_session(self):
        response = self.client.post(
            "/",
            {"name": "recepcion", "password": "incorrecta"},
        )

        self.assertRedirects(response, "/home/", fetch_redirect_response=False)
        self.assertNotIn("user_id", self.client.session)

    def test_login_allows_password_over_ten_characters(self):
        response = self.client.post(
            "/",
            {"name": "analista", "password": "Analista123!"},
        )

        self.assertRedirects(response, "/home/", fetch_redirect_response=False)
        self.assertEqual(self.client.session["user_role"], "Analista")

    def test_protected_path_redirects_without_session(self):
        for path in ("/home/", "/profile/", "/room/", "/booking/", "/stadistics/"):
            with self.subTest(path=path):
                self.assertRedirects(
                    self.client.get(path), "/", fetch_redirect_response=False
                )

    def test_protected_path_works_with_session(self):
        self.client.post("/", {"name": "recepcion", "password": "Recepcion123!"})

        self.assertEqual(self.client.get("/home/").status_code, 200)
        self.assertEqual(self.client.get("/profile/").status_code, 200)

    def test_logout_flushes_session(self):
        self.client.post("/", {"name": "recepcion", "password": "Recepcion123!"})

        response = self.client.get("/logout/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("user_id", self.client.session)


class SignUpViewTests(TestCase):
    def test_creates_user_with_hashed_password(self):
        response = self.client.post("/signup/", {
            "name": "nuevo",
            "password": "Nuevo12345",
            "role": "Analista",
        })

        self.assertRedirects(response, "/", fetch_redirect_response=False)
        user = ICUser.objects.get(name="nuevo")
        self.assertEqual(user.role, "Analista")
        self.assertTrue(bcrypt.checkpw(b"Nuevo12345", user.password.encode()))

    def test_rejects_invalid_role(self):
        form = SignUpForm({
            "name": "nuevo",
            "password": "Nuevo12345",
            "role": "administrador",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)
