from flask import Response, jsonify
from api import db
from api.errors import errors_bp #import blueprint z pliku int.py errors_bp

class ErrorResponse: # klasa w celu zwrócenia danych w formacie json, jest to implementacja obiektu response z dołu postman
    #funkcja odpowieda za wygląd odpowiedzi w body response
    def __init__(self, message: str, http_status: int):# przyjmuje 2 argumenty: message oraz http_status
        # atrybut payload zwracany w ciele odpowiedzi serwera (body response), słownik z 2 kluczami
        self.payload ={
            'success': False,
            'message': message
        } 
        self.http_status = http_status

    def to_response(self) -> Response:#metoda ta będzie przekształcać instancję klasy ErrorResponse na obiekt response, 
        #Response to oczekiwana wartość, 
        #funkcja odpowiada za przerobienie powyższych danych na format json
        response = jsonify(self.payload)
        response.status_code =self.http_status
        return response



#400 bad request, brak jakiś danych w zapytaniu http, działa
@errors_bp.app_errorhandler(400)#dla kodu odpowiedzi 400
def bad_request_error(err):# jako argument przyjmuje rzucony wyjątek (err), funkcja się uruchomi w przypadku wystąpienia kodu odpowiedzi 404
    # inaczej wyciągana informacja o wiadomości, bo w tym przypadku obiekt err jest tworzony przez pakiet marshmallow
    messages = err.data.get('messages', {}).get('json', {})
    # odwołanie do obiektu err, data jest słownikiem, z którego wyciągam klucz messages, gdy tego klucza nie ma to zwraca pusty słownik
    #messages też jest słownikiem dlatego ponownie korzystam z funkcji get i wyciągam klucz json, gdy klucza nie ma to zwraca pusty słownik
    return ErrorResponse(messages, 400).to_response()


# 401 unauthorized, brak autoryzacji w bazie danych
@errors_bp.app_errorhandler(401)#dla kodu odpowiedzi 401, instancja aplikacji app z metodą errorhandler
#error handler argument to kod opowiedzi albo rzucony wyjątek
def unauthorized_error(err):# jako argument przyjmuje rzucony wyjątek (err), funkcja się uruchomi w przypadku wystąpienia kodu odpowiedzi 404
    return ErrorResponse(err.description, 401).to_response()


# 404 not found, brak rekordu w bazie danych, działa
@errors_bp.app_errorhandler(404)#dla kodu odpowiedzi 404, instancja aplikacji app z metodą errorhandler
#error handler argument to kod opowiedzi albo rzucony wyjątek
def not_found_error(err):# jako argument przyjmuje rzucony wyjątek (err), funkcja się uruchomi w przypadku wystąpienia kodu odpowiedzi 404
    return ErrorResponse(err.description, 404).to_response()




# 409 not found, conflict
@errors_bp.app_errorhandler(409)
def conflict_error(err):
    return ErrorResponse(err.description, 409).to_response()



#415 unsupported media, zły format danych w zapytaniu, np zamiast json to wpisujemy tekst (brak ustawionego content type na json), nie działa
@errors_bp.app_errorhandler(415)#dla kodu odpowiedzi 415 -unsupported media type
def unsupported_media_type_error(err):# jako argument przyjmuje rzucony wyjątek (err), funkcja się uruchomi w przypadku #wystąpienia kodu odpowiedzi 415
    return ErrorResponse(err.description, 415).to_response()



#500 internal error server, błąd podczas wysyłania query do naszej bazy danych, nie wiem czy działa
@errors_bp.app_errorhandler(500)
def internal_server_error(err):# jako argument przyjmuje rzucony wyjątek (err), funkcja się uruchomi w przypadku 
    db.session.rollback()# resetuje sesję db
    return ErrorResponse(err.description, 500).to_response()