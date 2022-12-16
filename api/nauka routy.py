from api import app
from api.models import Author, AuthorSchema
from flask import request


@app.route('/api/v1/authors', methods = ['GET'])
def get_authors():




    #   1...wyświetlenie po prostu wszystkich autorów
    authors = Author.query.all() #zapytanie do bd o wszystkich autrów
    author_schema = AuthorSchema(many=True) #zastosowanie walidacji danych, przyjmuje wiele danych

    #return jsonify
    ({
        'success': True,
        'data':author_schema.dump(authors),#dump odpowiada za serializację danych - obiekt ->json
        'number_of_records': len(authors)
    })





    #   2...pobranie tylko wybranych rekordów
    authors = Author.query.all() 
    schema_args = Author.get_schema_args(request.args.get('fields')) # określenie fields, get schema args tworzy dynamicznie argumenty(słownik) zamiast only
    author_schema = AuthorSchema(**schema_args) #zastosowanie walidacji danych, przyjmuje dane zgodne z fields
    
    #return jsonify
    ({
        'success': True,
        'data':author_schema.dump(authors),#dump odpowiada za serializację danych - obiekt ->json
        'number_of_records': len(authors)
    })
        





    #   3...sortowanie danych
    query = Author.query #dynamiczne budowanie obiektu query, dlatego skasowano all() lub order_by(), obiekt authors zmieniam na query
    query = Author.apply_order(query, request.args.get('sort'))#przekazany jest obiekt query oraz dane z value (sort)
    authors = query.all() #zwrócenie wszystkich rekordów w oparciu o nowe query z funkcją sort
    author_schema = AuthorSchema(many=True)

        #return jsonify
    ({
        'success': True,
        'data':author_schema.dump(authors),#dump odpowiada za serializację danych - obiekt ->json
        'number_of_records': len(authors)
    })



    #   4...sortowanie - wybranie rekordów zawierających imie Andrzej key=name value=Andrzej
    query = Author.query #dynamiczne budowanie obiektu query
    query = Author.apply_filter_1(query, request.args) #metoda filturjąca 1
    authors = query.all()
    author_schema = AuthorSchema(many=True)

        #return jsonify
    ({
        'success': True,
        'data':author_schema.dump(authors),#dump odpowiada za serializację danych - obiekt ->json
        'number_of_records': len(authors)
    })







    #   5...sortowanie danych ze znakami > <

    query = Author.query #dynamiczne budowanie obiektu query
    query = Author.apply_filter_2(query, request.args) #metoda filturjąca 2
    authors = query.all()
    author_schema = AuthorSchema(many=True)

        #return jsonify
    ({
        'success': True,
        'data':author_schema.dump(authors),#dump odpowiada za serializację danych - obiekt ->json
        'number_of_records': len(authors)
    })






    @staticmethod
    def apply_filter_1(query: query, params: ImmutableDict ) -> query:
        for param, value in params.items(): # params ma metodę items która pozwoli pobrać nazwę parametru url oraz jego wartość
            if param not in {'fields','sort'}:#musimy pominąć params fields oraz sort, bo dla nich mamy oddzielne funkcje
                column_attr = getattr(Author, param, None) #nazwa kolumny po której będzie filtrowane, wyciągam z klasy author atrybut param, jeżeli go nie ma to będzie wartość None
                if column_attr is not None:#sprawdzam czy jest taka kolumna w tabeli
                    if param == 'birth_date':
                        try:#trzeba przekonwertować stringa na date
                            value = datetime.strptime(value, '%d-%m-%Y').date() 
                        except ValueError: 
                            continue # continue powoduje pominiecie filtrowania
                    query = query.filter(column_attr == value)#tworzę nowe query poprzez zastosowanie metody filter, do metody przekazuję nazwę kolumny która jest równa wartość value z adresu URL
        return query


    @staticmethod
    def apply_filter_2(query: query, params: ImmutableDict ) -> query:
        for param, value in params.items(): # params ma metodę items która pozwoli pobrać nazwę parametru url oraz jego wartość
            if param not in {'fields','sort'}:#musimy pominąć params fields oraz sort, bo dla nich mamy oddzielne funkcje
                operator = '=='
                match = COMPARISON_OPERATORS_RE.match(param)#schemat wprowadzonych danych
                if match is not None:# jeżeli znaleziono gte, gt, lte lub lt w parametrach
                    param, operator = match.groups()
                column_attr = getattr(Author, param, None) #nazwa kolumny po której będzie filtrowane, wyciągam z klasy author atrybut param, jeżeli go nie ma to będzie wartość None
                if column_attr is not None:#sprawdzam czy jest taka kolumna w tabeli
                    if param == 'birth_date':
                        try:#trzeba przekonwertować stringa na date
                            value = datetime.strptime(value, '%d-%m-%Y').date() 
                        except ValueError: 
                            continue # continue powoduje pominiecie filtrowania
                    filter_argument = Author.get_filter_argument(column_attr, value, operator)
                    query = query.filter(filter_argument)#tworzę nowe query poprzez zastosowanie metody filter, do metody przekazuję nazwę kolumny która jest równa wartość value z adresu URL
        return query
