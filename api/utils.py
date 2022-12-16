from flask import request # celu sprawdzenia co jest wpisane w zapytaniu request - górna część postman, jeżeli nie ma zaznaczonego json to jest wartość None
from werkzeug.exceptions import UnsupportedMediaType #werkzeug.exceptions to wbudowany moduł we flask, unsupportedmediatype to wyjątek
from functools import wraps #dekorator wraps odpowiada za ustawienie poprawnej nazwy funkcji, w tym przypadku wrapper

#tworze dekorator validate_json_content_type - sprawdzi czy nagłówek content type ustawiony jest na json
def validate_json_content_type(func):#jako argument przekazuję funkcję wrpapper
    @wraps(func)
    def wrapper(*args, **kwargs):#przekazuje argumenty args/kwargs, bo nie wiem ile będzie argumentów oraz ile będzie klucz=wartość
        # ztymi argumentami funkcja wrapper zostanie wywołana i przekazana do dekoratora validate_json_content_type
        data = request.get_json() #sprawdzam czy w zapytaniu request (górna część postman)jest json 
        #jak nie ma to jest wartość none i wyskauje bład 
        if data is None: #jeżeli wartość to none to wyświetli się wyjątek
            raise UnsupportedMediaType('Content type must be application/json')# bład 
        return func(*args,**kwargs) # tutaj przekazywane są argumenty args i kwargs, func jest wywoływana
    return wrapper #zwrócenie funkcji wraper bez jej wywoływania