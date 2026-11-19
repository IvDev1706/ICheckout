"""
Settings para ejecutar la suite de pruebas.

El usuario MySQL del proyecto solo tiene privilegios sobre la base `icheckout`,
por lo que no puede crear `test_icheckout`. Esta configuracion usa SQLite en
memoria para las pruebas:

    python manage.py test --settings=icheckout.settings_test
"""

from .settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
