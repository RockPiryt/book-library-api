# do wyrażeń regex - comparison operators
import re

#get_filter
from sqlalchemy.orm.attributes import InstrumentedAttribute #wykorzystywane do metody get filter argument
from sqlalchemy.sql.expression import BinaryExpression #wykorzystywane do metody get filter argument

from flask_sqlalchemy.model import DefaultMeta
from flask_sqlalchemy.query import Query

#do pagination
from typing import Tuple # import krotki do funkcji get_pagination
from flask import request, url_for, jsonify #stosowant do paginacji
#from config import Config #config.PER_PAGE zbędne gdy ustawiamy 2 środowiska developerskie i testowe

#do validate_json
from functools import wraps 

#żeby nie było błędu z config.PER_PAGE w pagination, bo teraz będziemy wczytywać różne configuracje
from flask import current_app

#do token_required
from flask import abort
import jwt



COMPARISON_OPERATORS_RE = re.compile(r'(.*)\[(gte|gt|lte|lt)\]') #skompilowanie wyrażenia regex przy użyciu modułu re z python
#czyli przetłumaczenia regex na język python


def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            request.json
        except:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 415
        return f(*args, **kw)
    return wrapper

def token_required(func): #jako argument pzyjmuje funkcje
    @wraps(func)
    def wrapper(*args, **kwargs):#parametry do wrappera to argumenty (args, kwars) funkcji FUNC
        token = None # obiekt token
        auth = request.headers.get('Authorization')#wyciągamy wartość nagłówka authorization
        if auth: #sprawadzam czy zamienna auth posiada jakąś wartość
            token = auth.split(' ')[1]#jeżeli nie jest pusta to wyciągamy token, [1] oznacza obiekt token drugi element,spli to spacjat
        if token is None:#jeżeli brak tokena to bład
            abort(401, description='Missing token. Please login or register')
        #jeżeli klient przesłał token to następuje jego walidacja
        try:
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])#rozkodujemy token

        #możliwe błędy
        except jwt.ExpiredSignatureError:#jeżeli toknowi wygasła ważność
            abort(401, description='Expired token. Please login to get new token')
        except jwt.InvalidTokenError:#jeżeli token jest niepoprawny
            abort(401, description='Invalid token. Please login or register')

        #jeżeli nie ma błędów to metoda decode zwraca zmienna payload
        #payload w model.py zawiera 2 informacje: user_id oraz exp(date trwałości tokena)
        #do każdego zapytnia POST,PUT,DELETE dołaczymy informacje user_id
        else:
            return func(payload['user_id'], *args, **kwargs) #do funkcji przekazujemy poayload z inforamcją o user_id (toekn przypisany do usera) oraz pozostałe elementy
    return wrapper


#metoda w zależności od zapytania http będzie dynamicznie tworzyć argumenty do klasy AythorSchema
def get_schema_args(model: DefaultMeta) -> dict:
    schema_args = {'many': True}
    fields = request.args.get('fields')#wyciągniecie fileds za pomocą request, informacje będą w url
    if fields:
        schema_args['only'] = [field for field in fields.split(',') if field in model.__table__.columns]# model reprezentuje clasę Author lub Book
    return schema_args





def apply_order(model: DefaultMeta, query: Query) -> Query:
    sort_keys = request.args.get('sort')#wyciągniecie sort za pomocą request, informacje będą w url
    if sort_keys:
        # pętla po kluczach oddzielonych przecinkiem
        for key in sort_keys.split(','):
            desc = False  # zmienna w przyapdku minusa przed kluczem do sortowania
            # sprawdzenie czy klucz zaczyna się od minusa (jeżeli tak to sortowanie malejąco)
            if key.startswith('-'):
                key = key[1:]  # nowa wartość z pominięciem znaku -
                desc = True

                # zmiana stringa na obiekt sqlalchemy
            # nazwa kolumny po której będzie sortowane, wyciągam z klasy author atrybut key, jeżeli go nie ma to będzie wartość None
            column_attr = getattr(model, key, None)
            if column_attr is not None:  # jeżeli istnieje taka kolumna w bazie danych
                # tworzę nowy obiekt query z sortowaniem po kolumnie, .desc metoda sortująca dane malejącp
                query = query.order_by(
                    column_attr.desc()) if desc else query.order_by(column_attr)
    return query


def _get_filter_argument(column_name: InstrumentedAttribute, value: str, operator: str) -> BinaryExpression: #funkcja prywatna
    #tworzę słownik który w zależności od słowa będzie tworzył odpowiedni znak
    operator_mapping={
        '==':column_name == value,
        'gte':column_name >= value,
        'gt':column_name > value,
        'lte':column_name <= value,
        'lt':column_name < value
    }
    return operator_mapping[operator] #utworzenie odpowiedniego znaku >=,>,<,<= w zależności od przesłanego operatora np gte, gt lte lt


def apply_filter(model: DefaultMeta, query: Query ) -> Query:
    #będziemy iretować po każdym parametrze w url, jeżeli nazwa params pasuje do nazwy kolumny tabeli to do metody filter w obiekcie query dodamy odpowiedni argument
    for param, value in request.args.items(): # params ma metodę items która pozwoli pobrać nazwę parametru url oraz jego wartość
        if param not in {'fields','sort', 'page', 'limit'}:#musimy pominąć params fields oraz sort, bo dla nich mamy oddzielne funkcje
            operator = '==' # przypisanie domyślnej wartości, która może być zmieniana jeżeli pojawi się operator gte, gt, lte, lt
            match = COMPARISON_OPERATORS_RE.match(param)# wprowadzone dane w request w value, za pomocą wyrażenia regularnego comparison sprawdzam czy w reuqest wystąpiła gte, gt, lte, lt we wprowadzonych params
            #metoda match przeszukuje we wprowadzonych danych (param) czy występuje jakies (słowo gte, lte, lt) zgodnie ze wzorcem wyrazenia regularnego Comparison_operators
            #gdy klient nie wprowadzi żadnego gte,gt, lte lub lt to match=None, gdyż nie udało się dopasować wyrażenia regularnego  do nazwy parametru
            if match is not None:# jeżeli znaleziono gte, gt, lte lub lt w parametrach
                param, operator = match.groups() # do zmiennej param przypiszę nową wartość oraz utworzymy zmienną operator , 
                #operator przechowuje (gte, gt,lt lub lte)
                #wykorzystuję metodę match z grups która zwróci krotkę, krotka zostanie wypakowana do param i do operator
                # w zależności od przechowywanej danej w zmiennej operator(gte,gt,lte lub lt) będzie dynamicznie tworzona wartość do metody filter z query
            column_attr = getattr(model, param, None) #nazwa kolumny po której będzie filtrowane, wyciągam z klasy author atrybut param, jeżeli go nie ma to będzie wartość None
            if column_attr is not None:#sprawdzam czy jest taka kolumna w tabeli
                value = model.additional_validation(param, value)
                if value is None:
                    continue
                filter_argument = _get_filter_argument(column_attr, value, operator)# do metody get_filter_arg przekazuję nazwę kolumny, wartość oraz wartość operatora
                # klasę author przekazuję do query które będzie filtrowało bazę danych
                query = query.filter(filter_argument)# do metody filter przekazuję dynamicznie co jest wpisane w param czyli np birth_date[gte]
                #(column_attr == value) #tworzę nowe query poprzez zastosowanie metody filter, do metody przekazuję nazwę kolumny która jest równa wartość value z adresu URL
    return query



def get_pagination(query: Query, func_name:str) -> Tuple[list, dict]: #funkcja będzie zwracać krotkę , 1 element to lista rekordów dostępna na danej stronie(paginate_obj.items), 
    #2 element pagination informuje o sposobie paginacji
    page = request.args.get('page', 1, type=int)# albo wpisany numer strony albo 1 jako strona default
    limit = request.args.get('limit', current_app.config.get('PER_PAGE', 5), type=int)# albo wpisany limit albo limit z pliku config
    #PER_PAGE z pliku config lub jak brak informacji to wartość domyślna 5
    params = { key: value for key, value in request.args.items() if key !='page'}#comprehension dict
    paginate_obj = query.paginate(page = page, per_page = limit, error_out = False)
    pagination={
        'total_pages': paginate_obj.pages,
        'total_records': paginate_obj.total,
        'current_page': url_for(func_name, page=page, **params)#get_authors nazwa funkcji dla http 
    }# page i params dodane do adresu url
    # params to wartości dodane przez użytkownika np pola sort/fields
    if paginate_obj.has_next:
        pagination['next_page'] = url_for(func_name, page=page+1, **params)#jeżeli warunek jest spełniony dodaje nowy klucz do obiektu pagination, wrtość podana przez url

    if paginate_obj.has_prev:
        pagination['previous_page'] = url_for(func_name, page=page-1, **params)

    return paginate_obj.items, pagination




#'authorsblue.get_authors'
