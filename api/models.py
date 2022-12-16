
import jwt # pakiet do tworzenia tokena
from api import db
from datetime import datetime, date, timedelta #timedelta do generowania tokena
from flask import current_app # do generowania tokena w oparciu o aktulany congifg
from marshmallow import Schema, fields, validate, validates, ValidationError

from werkzeug.security import generate_password_hash # do zahasowania hasła w clasie User
from werkzeug.security import check_password_hash # do sprawdzenia poprawności  hasła w clasie User

#niepotrzebne albo złe
#from werkzeug.datastructures import ImmutableDict - skasowanie z metody apply_filter
#from api.authors import get_author niepotrzebne
#from flask_sqlalchemy import query nie działa
#from config import Config
#from flask import request, url_for #stosowant do paginacji
#from flask_sqlalchemy.query import Query

class Author(db.Model):
    __tablename__ = 'tworcy' #nazwa tabeli, to się wyświetla w MySQL
    id = db.Column(db.Integer, primary_key = True)#klucz podstawowy
    name = db.Column(db.String(50), nullable=False)#nullable - trzeba wpisać wartość
    last = db.Column(db.String(50), nullable=False)#nullable - trzeba wpisać wartość
    birth_date = db.Column(db.Date, nullable=False)#nullable - trzeba wpisać wartość
    books = db.relationship('Book', back_populates='author', cascade='all, delete-orphan')# 1 argument to nazwa classy Book, drugie to author zgodne ze zmienną w klasie book
    #casacade - jeżeli skasowany zostanie autor to zostaną skasowane wszystkie przypisane do niego ksiązki

    def __repr__(self):#tekstowa reprezentacja naszego modelu
        return f'{self.__class__.__name__}>:{self.name}{self.last}'#nie tworzymy metody init, gdyż ta metoda jest tworzona niejawnie przez sql alchemy, 
    #wszystkie przekazane do niej argumenty są przechowywane w zmiennej **kwargs, musimy przekazać wszystkie dane w postaci klucz=wartość
#nazwa naszej klasy, odwołanie do instacji, do atrybutu klass oraz atrybutu name

    @staticmethod
    def additional_validation(param: str, value: str) -> date:
        if param == 'birth_date':# w przypadku birth_date to nie string tylko date
            try:#trzeba przekonwertować stringa na date
                value = datetime.strptime(value, '%d-%m-%Y').date() #do obiektu datetime strptime (zmana string na datetime) daje 2 argumenty, value oraz format danych, na koniec konwertuje za pomocą .date do formatu date zamist datetime 
            except ValueError: #kiedy byłby błąd z datą, data w nieporawnym formacie
                value = None
        return value
     
   # @staticmethod
   # def apply_filter_1(query: query, params: ImmutableDict ) -> query:
        #for param, value in params.items(): # params ma metodę items która pozwoli pobrać nazwę parametru url oraz jego wartość
            #if param not in {'fields','sort'}:#musimy pominąć params fields oraz sort, bo dla nich mamy oddzielne funkcje
                #column_attr = getattr(Author, param, None) #nazwa kolumny po której będzie filtrowane, wyciągam z klasy author atrybut param, jeżeli go nie ma to będzie wartość None
                #if column_attr is not None:#sprawdzam czy jest taka kolumna w tabeli
                    #if param == 'birth_date':
                        #try:#trzeba przekonwertować stringa na date
                            #value = datetime.strptime(value, '%d-%m-%Y').date() 
                        #except ValueError: 
                            #continue # continue powoduje pominiecie filtrowania
                    #query = query.filter(column_attr == value)#tworzę nowe query poprzez zastosowanie metody filter, do metody przekazuję nazwę kolumny która jest równa wartość value z adresu URL
        #return query

    #@staticmethod
   # def apply_filter_2(query: query, params: ImmutableDict ) -> query:
       # for param, value in params.items():
            #if param not in {'fields','sort'}:
                #operator = '=='
                #match = COMPARISON_OPERATORS_RE.match(param)#schemat wprowadzonych danych
                #if match is not None:# jeżeli znaleziono gte, gt, lte lub lt w parametrach
                    #param, operator = match.groups()
                #column_attr = getattr(Author, param, None) 
                #if column_attr is not None:
                    #if param == 'birth_date':
                        #try:
                           # value = datetime.strptime(value, '%d-%m-%Y').date() 
                        #except ValueError:
                            #continue
                    #filter_argument = Author.get_filter_argument(column_attr, value, operator)# do metody get_filter_arg przekazuję nazwę kolumny, wartość oraz wartość operatora, czyli dane potrzebne funkcji get_filter_arg ->zobacz na górze
                    #query = query.filter(filter_argument)# do metody filter przekazuję dynamicznie co jest wpisane w param czyli np birth_date[gte]
        #return query
  

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    isbn = db.Column(db.BigInteger, nullable=False, unique=True)# duża liczba bo 13 liczb, unique znaczy że wartość niepowtarzalna
    number_of_pages = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('tworcy.id'), nullable=False)
    #obcy klucz jako argument nazwa tabeli tworcy oraz nazwa kolumny id

    #ustawienie relacji pomiędzy wieloma książkami books a 1 autorem
    author = db.relationship('Author', back_populates='books')#to jest obiekt relacji, 1 argument to nazwa klasy Author, 
    #backpopulates=books przechowuje informacje o relacji

    #reprezentacja tekstowa classy Book
    def __repr__(self):
        return f'{self.title} - {self.author.name} {self.author.last}'
        #w tym przypadku zmienna author jest obiektem i poprzez relację mamy dostęp do wszytskich atrybutów classy Author

    @staticmethod # funkcja wymagana w metodzie apply_filter, tu nie ma co sprawdzać ale funkcja musi być
    def additional_validation(param: str, value: str) -> str:
        return value

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)

    #funkcja do hashowania hasła
    @staticmethod
    def generate_hashed_password(password: str) ->str:
        return generate_password_hash(password)

    #funkcja do generowania tokena jwt z terminem ważności
    def generate_jwt(self):
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(minutes=current_app.config.get('JWT_EXPIRED_MINUTES', 30))
        }
        return jwt.encode(payload, current_app.config.get('SECRET_KEY'))#wyciągnięcie zakodowanego metodą jwt tokena
        # jako argumenty przekazuję id użytkownika i termin ważności dla tokena(payload) oraz ustawienia z aplikacji (secret_key)
        #encode zwraca bytes, ale od pyjwt 2.0 już są stringi więc nie potrzeba decodować rouecie auth_bp

    #metoda sprawdzająca poprawność hasła
    def is_password_valid(self, password)-> bool: #bool= boolean
        return  check_password_hash(self.password, password) #self.password to zahasowane hasło w bd, passowrd drugie to hasło sprawdzane


class AuthorSchema(Schema): #dziedziczy po klasie Schema z pakietu Marshmallow, odpowiada za stworzenie schematu, 
    #dzięki któremu dane z Author będą przekształcane na format json
    #AuthorSchema będzie odpowiadać za serializację danych oraz za ich walidację, serializacja= zamiana obiektów na tekst
    id = fields.Integer(dump_only=True)# dump-only oznacza ze id będziemy wykorzystywać podczas tylko podczas serializacji danych, 
    #tylko podczas metody dump, id będzie automatyczne, nie trzeba wprowadzać
    # required wymaga aby dane były wysyłane metodą post, jeżeli dane nie zostaną podane to nie przejdzie walidacji
    name = fields.String(required=True, validate=validate.Length(max=50))#gdy pominięte to pojawi się wyjątek validaton error
    last = fields.String(required=True, validate=validate.Length(max=50))
    birth_date = fields.Date('%d-%m-%Y', required=True)
    books = fields.List(fields.Nested(lambda:BookSchema(exclude=['author']))) #pole typu lista do którego przekazuję powiazanie, 
    #bo może być kilka książek a nie 1 autor
    # chce mieć wszystkie informacje o książe bez informacji o autorze

    #własna implementacja funkcji validującej, obiekt używamy jako dekorator@
    #sprawdzimy czy data jest mniejsza niż aktualna data
    @validates('birth_date')
    def validate_birth_date(self, value):#value wartość przekazana do parametru birth_date, wartość będzie przekonwertowana na obiekt date
        if value > datetime.now().date(): #obiekt datetime z data dzisiejszą przekonwertowany na date, jeżeli spełniony to pojawi się błąd
            raise ValidationError(f'Brith_date must be lower than {datetime.now().date()}')

class BookSchema(Schema):
    id = fields.Integer(dump_only=True)# dump-only oznacza ze id będziemy wykorzystywać podczasserializacji danych, id będzie automatyczne, nie trzeba wprowadzać
    title = fields.String(required=True, validate=validate.Length(max=50))
    isbn = fields.Integer(required=True)
    number_of_pages = fields.Integer(required=True)
    description = fields.String()
    author_id = fields.Integer(load_only=True)#load_only=true pole id nie będzie wykorzytywane w przypadku użycia metody dump
    author = fields.Nested(lambda:AuthorSchema(only=['id', 'name', 'last'])) #przekazanie info z AuthorSchema jako zmienna author
    #lambda to funkcja anonimowa, tylko raz wykonanie
    #only określa interesujące nas wartości

    @validates('isbn')# własny walidator czy isbn ma 13 liczb - nie działa
    def validate_isbn(self, value):
        if len(str(value)) != 13: #zmiana integer na string aby skorzystać z funkcji len
            raise ValidationError('ISBN must contains 13 digits') # validationError z pakietu Marshmallow


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(max=255))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=255))#load pominięcie podczas serializacji
    creation_date = fields.DateTime(dump_only=True)#pole wykorzytywane tylko podczas serializacji


class UserPasswordUpdateSchema(Schema):
    current_password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=255))
    new_password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=255))



author_schema = AuthorSchema()#utworzenie zmiennej author schema (instancja klasy AuthorSchema) bo będzie wielokronie używana
book_schema = BookSchema()
user_schema = UserSchema()
user_password_update_schema = UserPasswordUpdateSchema()

