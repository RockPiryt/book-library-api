#ogólne ustawienia dla testów automatycznych

import pytest
from api import create_app, db
from api.commands.db_manage_commands import add_data

#stworzenie instancji app dla środ. testowego
@pytest.fixture
def app():
    app = create_app('testing')#stworznie instacji aplikacji z konfiguracją przeznaczoną dla środ. testowego, jako argument przekazuję nazwę configu

    #utworzenie bazy danych
    #wewnątrz konekstu aplikacji tworzę bazę danych
    with app.app_context():
        db.create_all()#utworzy bazę danych i niezbędne tabele

    yield app #zwróci obiekt app do funkcji testującej, po każdym teście chce usunąć bazę danych, funkcja testująca wykonana zadanie poniżej

    app.config['DB_FILE_PATH'].unlink(missing_ok=True)
    # ten atrybut db_file_path przechowuje obiekt PATH, dlatego może użyć metody unlink aby usunąć plik
    #mising_ok=True - jeżeli brak pliku to nie zostanie rzucony żaden wyjątek



#stworzenie clienta dla danej instancji app 
@pytest.fixture
#fixture jest napierw robiony dopiero później funkcja testująca
def client(app):#korzystamy z obiektu app
    with app.test_client() as client: # ta metoda zwróci clienta który będzie dostępny w obrębie danego contextu
        yield client


#fixture rejestrujący usera (client jest niezalogowany)
@pytest.fixture
def user(client):#user jest rejestrowny przez clienta
    user = {
                'username':'test',
                'password': '123456',
                'email':'test@gmail.com'
            }#dane dla user
    client.post('/api/v1/auth/register', json=user)#dane user przesyłam jako json do funkcji rejestrującej
    return user


#fixture logujący usera i zwaracjący token
@pytest.fixture
def token(client, user):#fixture client wyłowyny 1x nie 2x, user 1x, można to zmienić ale dla nas ok
    #logowanie do istniejącego użytkownika - user- wysyłamy zapytanie post
    #dane do logowania wyciągamy z fixture user
    response = client.post('/api/v1/auth/login', json={
        'username': user['username'],
        'password': user['password']
    })

    #zwracamy wartość tokena
    return response.get_json()['token']#wyciągamy z body klucz json 'token'


#fixture ładujący dane z pliku json
@pytest.fixture
def sample_data(app):
    runner = app.test_cli_runner()
    runner.invoke(add_data) #korzystamy z metody invoke, jako argument przekazuję add_data z db_manage_comands.py 


#fixture tworzący author
@pytest.fixture
def author():
    return{
        'name':'Adam',
        'last':'Mickiewicz',
        'birth_date': '24-12-1798'
    }