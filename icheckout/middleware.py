from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

#middleware custom para validar la sesion
class MySessionValidationMiddleware:
    def __init__(self, get_response:HttpResponse):
        #respuesta a peticion get
        self.get_response = get_response

    def __call__(self, request:HttpRequest):
        #rutas protegidas
        protected_paths = ('/room/','/profile/','/logout/','/home/','/booking/')

        #validacion de rutas
        if request.path.startswith(protected_paths):
            #obtener el id de usuario
            user_id = request.session.get("user_id")
            
            #validamos la sesion
            if not user_id:
                return redirect("/")

        #pasamos la peticion
        response = self.get_response(request)
        
        #retornamos la respuesta
        return response   