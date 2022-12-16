
import json
from pathlib import Path # potrzebna do wyciągnięcia ścieżki pliku authors z folderu samples
from datetime import datetime

from api import db
from api.models import Author, Book
from api.commands import db_manage_cmd_bp

def load_json_data(file_name: str) -> list:
    json_path = Path(__file__).parent.parent/'samples'/ file_name # tutaj ścieżka pliki
    with open(json_path) as file: # wykorzystuje contex managera w celu pobrania danych znajdujących sie w tym pliku , zmienna to file
        data_json = json.load(file) # zmienna będzie przechowywała pobrane dane używamy modułu json i metody load,  
    return data_json

@db_manage_cmd_bp.cli.group()#pakiet click, grupa komend
def db_manage():#nazwa użyta jako dekorator komend
    """Database managment commands"""#komentarz widoczny przy komendzie
    pass

@db_manage.command()#komenda dodająca dane, subkomenda
def add_data():
    """Add sample data to database"""
    try:
        data_json = load_json_data('authors.json') # stosuję ogólną funkcję laod_json i wczytuję plik authors.json
        for item in data_json: #pętla wyświetlająca dane ze zmiennej data_json(zawiera informacje z pliku author.json)
            item['birth_date'] = datetime.strptime(item['birth_date'], '%d-%m-%Y').date()
            author = Author(**item)# gwiazdki oaznaczają wypakowanie obiektu item, item jest słownikiem, 
            #dlatego poszczególne  klucze w tym słowniku zostaną przyporządkowane do atrybutów w kalsie author
            db.session.add(author)#dodanie do sesji wypakowanych danych

        data_json = load_json_data('books.json') # stosuję ogólną funkcję laod_json i wczytuję plik books.json
        for item in data_json:
            book = Book(**item)# gwiazdki oaznaczają wypakowanie obiektu item, item jest słownikiem, 
            #dlatego poszczególne  klucze w tym słowniku zostaną przyporządkowane do atrybutów w kalsie author
            db.session.add(book)#dodanie do sesji wypakowanych danych

        db.session.commit()# zatwierdzenie danych w bazie, poza pętlą
        print('Data has been successfuly added to database')

    except Exception as exc:
         print("Unexpected error{}".format(exc))


@db_manage.command()#komenda usuwająca dane, subkomenda
def remove_data():
    """Remove all data from the database"""
    try:
        #db.session.execute('TRUNCATE TABLE tworcy')# wykonanie w bazie danych usumięcia, nie zadziała dla tabel z foregin_key

        db.session.execute('DELETE FROM books')#usunięcie wszystkich rekordów z tabeli
        db.session.execute('ALTER TABLE books AUTO_INCREMENT = 1') # wyzerowanie foregin_key

        db.session.execute('DELETE FROM tworcy')
        db.session.execute('ALTER TABLE tworcy AUTO_INCREMENT = 1')
        db.session.commit()
        print('Data has been successfuly removed from database')

    except Exception as exc:
         print("Unexpected error{}".format(exc))
