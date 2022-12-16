
from api import db
from flask import jsonify
from webargs.flaskparser import use_args # do funkcji create author,zwaliduje przesłane dane w zapytaniu http z 
#wykorzystaniem klasy author_schema i zwróci je w postaci słownika
from api.models import Author, AuthorSchema, author_schema
#from api.utils import validate_json_content_type #import dekoratora z utils
from api.uti import validate_json, get_schema_args, apply_order, apply_filter, get_pagination,token_required
#validate json do create author w celu sprawdzenia czy wprowadzane dane są w formacie json
from api.authors import authors_bp # import blueprint o nazwie authorsblue

@authors_bp.route('/authors', methods = ['GET']) # wyświetlenie wszystkich autorów, get jest domyślnie
# przekształcenie obiektów z bazy danych poprzez serializacje(obiekt na tekst) do formatu json
#AuthorSchema w tym przypadku odpowiada że obiekty z klasy Author z models.py są serializowane do formatu tekstowego json
def get_authors():
    #sortowanie danych
    query = Author.query#zapytanie do bazy danych w zmiennej
    schema_args = get_schema_args(Author)# przesłanie klasy Author jako model do funkcji w uti.py
    query = apply_order(Author, query)#dodanie metody odpowiedzialnej za sortowanie, pierwszy parametr to query, drugi to sort w params w postman
    query = apply_filter(Author, query)# obiekt query z funkcją filtrowania, nie podaje konkretnie args, bo można wpisać wszystko
    items, pagination = get_pagination(query, 'authorsblue.get_authors') #wypakowanie krotki Tuple z funkcji get_pagination, w zmiennej items są informacje o autorach dlatego nie potrzebna kolejna linijka
    #authors = query.all() #wyświetlenie wszystkich rekordy, items ma teraz info o autrach
    authors = AuthorSchema(**schema_args).dump(items)

    #wszyscy autorzy
    #authors = Author.query.all()#zapytanie do bazy danych o wszystkich authorów
    #author_schema = AuthorSchema(many=True)#many informuje marshmallow że będziemy przekazywać listę obiektów, instancja klasy AuthorSchema
    #only =[] - można wpisać klucze (id lub name)i po nich wyświetlać odpowiednie dane, ale trzeba za każdym razem zmieniać, nie jest dynamiczne dla bazy danych
    #pobranie określonych kluczy
    #zastsowanie metody get_schema_args z models.py, która dynamicznie tworzy argumenty do klasy AuthorSchema
    #authors = Author.query.all()#zapytanie do bazy danych o wszystkich authorów
    #schema_args = Author.get_schema_args(request.args.get('fields')) #stworzenie klasy Author z polami wybranymi w fields, 
    #żeby wiecdzieć jakie dane są w fields korzystam z obiektu request (górna część postman/zapytanie http) 
    # #i wyciągam co jest wpisane w polu fields, żenby móc wyświetlić autrów tylko z danymi spełniającymi dane w fields
    #author_schema = AuthorSchema(**schema_args) #zastosowanie do instancji Author Schema dynamicznie utworzonych argumentów schema args

    return jsonify({
            'success': True,
            'data': authors,# metoda dump przekształci dane z authors do json, lista obiektów w formacie json
            #dump odpowiada za serializację danych
            'number_of_records': len(authors),# podanie ilości rekordów
            'pagination': pagination

        })# słownik z 2 kluczami, 1 czy się powiodło, 2 z informacją o zasobie, odpowiedź http 200

@authors_bp.route('/authors/<int:author_id>', methods = ['GET']) # wyświetlenie pojedyńczego autora
def get_author(author_id:int):
    author = Author.query.get_or_404(author_id, description =f'Author with id {author_id} not found' )
    # funkcja ta zwróci informacje o rekordzie z routy lub 
    #zwróci informacje że nie znaleziono takiego rekordu, description pojawi sie w przypadku błędu
    return jsonify({
            'success': True,
            'data':author_schema.dump(author)
        })# f string aby móc dodać dodatkowe pole {author id}, odpowiedź http 200

@authors_bp.route('/authors', methods = ['POST']) # utworzenie nowego rekordu
@token_required
@validate_json
@use_args(author_schema, error_status_code=400)# dekorator, wartośc instancja klasy autor_schema z models.py
# zwaliduje przesłane dane w zapytaniu http z wykorzystaniem klasy author_schema i zwróci je w postaci słownika
def created_author(user_id:int, args: dict):# nowa funkcja !!!, parametry który przeszły przez schemat author_schema będą przechowywane w słowniku
    #jako argumenty przekazuję słownik 
    author = Author(**args)

    db.session.add(author)
    db.session.commit()
    

    #stara funkcja!!!
    #data = request.get_json()#będzie przecowywać wszystkie dane przesłane w body zapytania htttp
    #zmienne do przechowywania atrybutów
    #name = data.get('name') #zmienna date przechowuje słownik dlatego korzystam z funkcji get
    #last = data.get('last')
    #birth_date = data.get('birth_date')
    #author = Author(name=name, last=last, birth_date=birth_date)# stworzenie instancji klasy Author z models.py
    # przekazuje do tej klasy zmienne podane powyżej
    #db.session.add(author)
    #db.session.commit()
    return jsonify({
            'success': True,
            'data': author_schema.dump(author)
        }), 201 # odpowiedź http 201

@authors_bp.route('/authors/<int:author_id>', methods = ['PUT']) # aktualizacja istniejącego rekordu
@token_required
#@validate_json_content_type #sprawdzi czy wprowadzane dane są ustawione na json/appliacation
@validate_json
@use_args(author_schema, error_status_code=400)# zwaliduje przesłane dane w zapytaniu http z wykorzystaniem klasy author_schema i zwróci je w postaci słownika
#zmieniamy kod odpowiedzi z 422 na 400(bad request)

def update_author(user_id:int, args: dict, author_id: int):#args będzie przechowywał poprawnie zwalidowane dane w słowniku
    #ważna kolejność najpierw przekazujemy zwalidowane przez dekorator use_args dane a potem numer authora
    author = Author.query.get_or_404(author_id, description =f'Author with id {author_id} not found' )
    author.name = args['name']
    author.last = args['last']
    author.birth_date = args['birth_date']

    db.session.commit()

    return jsonify({
            'success': True,
            'data':author_schema.dump(author)
        })

@authors_bp.route('/authors/<int:author_id>', methods = ['DELETE']) # usunięcie istniejącego rekordu
@token_required
def delete_author(user_id:int, author_id:int):
    author = Author.query.get_or_404(author_id, description =f'Author with id {author_id} not found' )#wyciągnięcie z db authora
    db.session.delete(author)
    db.session.commit()

    return jsonify({
            'success': True,
            'data':f'Author with id {author_id} has been deleted'
        })