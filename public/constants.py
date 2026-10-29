#roles de usuario
USER_ROLES = ("recepcionista","Analista")

#modulos
USER_MODULES = {
    USER_ROLES[0]: [
        {
            "title": "Habitaciones",
            "description": "Cree, actualize, consulte y elimine las habitaciones del hotel y sus tipos",
            "picture": "assets/icheckout_room.png",
            "url": "/room/"
        },
        {
            "title": "Reservas",
            "description": "Cree, actualize, consulte y elimine las reservas de habitacion",
            "picture": "assets/icheckout_logo.png",
            "url": "/booking/"
        }
    ],
    USER_ROLES[1]: [
        {
            "title": "Reporteo",
            "picture": "assets/icheckout_logo.png",
            "description": "consulte las estadisticas del mes mediante reportes",
            "url": "/"
        },
        {
            "title": "Prediccion y deteccion (AI)",
            "picture": "assets/icheckout_logo.png",
            "description": "Revise deteccion de patrones y prediccion de cifras",
            "url": "/"
        }
    ]
}