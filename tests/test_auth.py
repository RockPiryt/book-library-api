#testy związane z bluprintem auth

import pytest


#zostanie wykonana def app, potem def client z conftest.py , a rezultat z def client zostanie przekazany do def test_registration
def test_registration(client):
    #przesyłamy zapytanie POST, wykorzystujemy clienta, odwołamy się do metody .post
    #1 argument to adres URL
    #2 argument to dane w zapytaniu http: username, password, email (dane mają być w json,)
    #json={} dzięki temu nie musimy ustawiać content-type na application json
    response = client.post('/api/v1/auth/register',
                            json={
                                'username':'test',
                                'password': '123456',
                                'email':'test@gmail.com'
                            })


#sprawdzamy czy serwer zwrócił poprawną odpowiedź 
#wyciągamy dane zapisane w ciele odpowiedzi (body respone) z serwera
    response_data = response.get_json() #wyciągamy do zmiennej (response_data) informacje json z obiektu response
    
    
    #sprawdzamy czy  kod odpowiedzi to 201 (created)
    assert response.status_code == 201 
    #sprawdzamy czy content type jest ustawiony na application/json
    assert response.headers['Content-Type'] == 'application/json' 
    #sprawdzamy zawartość w body repsonse
    assert response_data['success'] is True
    #sprawdzamy czy response_data zawiera token (wystarczy jakakolwiek wartość) dlatego bez dalszego opisu
    assert response_data['token'] 




#sprawdzamy czy w przypdaku niepoprawnego zapytania do clienta są dostarczone poprawne dane- 
# czyli że jest kod 400(bad request), succesz =False i nie wysłano tokena do clienta

#test sprawdzjacy czy zostały zawarte wszystkie niezbędne klucze  w ciele zapytania http

    #testujemy 3 scenariusze : pominiecie email, pominiecie password, pominiecie username
    # do tego możemy wykorzystać 3 oddzielne funkcje ale skorzystamy z parametrize

#dekorator parametrize umożliwia przesłanie kilku danych wejściowych do funkcji testujacej
# 1 argument w nawiasie to nazwy parametrów przekazanych do funkcji
# w data będą znadjować się wartośći przesłane w body zapytania http
# missing_field będzie nazwa klucza który nie zsostał umieszczony
#następnie umieszczamy te klucze (missing_field) jako parametry do funkcji test_registration_invalid data
#2 argument to wartości przypisane do data i missing_field - będzie to lista krotek
@pytest.mark.parametrize (
    'data, missing_field',
    [
        ({'username': 'test', 'password': '123456'},'email'),
        ({'username': 'test', 'email':'test@gmail.com'},'password'),
        ({'password': '123456', 'email':'test@gmail.com'},'username')
    ]
) 
def test_registration_invalida_data(client, data, missing_field):
    #przesyłamy zapytanie POST, wykorzystujemy clienta, odwołamy się do metody .post
    #1 argument to adres URL,#2 argument to dane w zapytaniu http: username, password, email (dane mają być w json,)
    response = client.post('/api/v1/auth/register',
                            json=data)


#wyciągamy dane zapisane w ciele odpowiedzi (body respone) z serwera
    response_data = response.get_json() #wyciągamy do zmiennej (response_data) informacje json z obiektu response
    
    
    #sprawdzamy czy  kod odpowiedzi to 400 (bad request)
    assert response.status_code == 400
    #sprawdzamy czy content type jest ustawiony na application/json
    assert response.headers['Content-Type'] == 'application/json' 
    #sprawdzamy zawartość w body repsonse czy jest na False w przypadku braku jakiegoś missing_field
    assert response_data['success'] is False
    #sprawdzamy czy token nie został już wysłany do clienta
    assert 'token' not in response_data
    #sprawdzamy missing_field jest w messeage w body response tak jak w postman
    assert missing_field in response_data['message']
    #sprawdzamy czy w missing_field (w kluczu message)przechowywyuje informacje Missing data for required field.
    assert 'Missing data for required field.' in response_data['message'][missing_field]





#test sprawdzajacy czy jak jest wyłączony content type to są wyświetlane prawidłowe dane dla klienta
def test_registration_invalida_content_type(client):
#przesyłam dane w zmiennej data nie json żeby nagłówek content type się sam nie załączył
    response = client.post('/api/v1/auth/register',
                            data={
                                'username':'test',
                                'password': '123456',
                                'email':'test@gmail.com'
                            })

    response_data = response.get_json() #wyciągamy do zmiennej (response_data) informacje json z obiektu response
    
    
    #sprawdzamy czy  kod odpowiedzi to 415 (unsupported media)
    assert response.status_code == 415
    #sprawdzamy czy content type jest ustawiony na application/json
    assert response.headers['Content-Type'] == 'application/json' 
    #sprawdzamy czy nie wyświetla się succeszz w body respone
    assert 'success' not in response_data
    #sprawdzamy czy token nie został już wysłany do clienta
    assert 'token' not in response_data





# test sprawdzjący kod 409 (conflict data) czy  nazwa użytkownika istnieje w bd
def test_registration_already_used_username(client, user):
    response = client.post('/api/v1/auth/register',
                            json={
                                'username': user['username'], 
                                'password': '123456',
                                'email':'test1234@gmail.com'
                            })

#email unikatowa wartość
#username pobrany z fixture user gdzie podany jest username

    response_data = response.get_json() #wyciągamy do zmiennej (response_data) informacje json z obiektu response
    
    
    #sprawdzamy czy  kod odpowiedzi to 409 (conflict data)
    assert response.status_code == 409
    #sprawdzamy czy content type jest ustawiony na application/json
    assert response.headers['Content-Type'] == 'application/json' 
    #sprawdzamy czy success jest False
    assert response_data['success'] is False
    #sprawdzamy czy token nie został już wysłany do clienta
    assert 'token' not in response_data





# test sprawdzjący kod 409 (conflict data) czy email istnieje w bd
def test_registration_already_used_email(client, user):
    response = client.post('/api/v1/auth/register',
                            json={
                                'username': 'test4', 
                                'password': '123456',
                                'email':user['email']
                            })

#username unikatowa wartość
#email pobrany z fixture user gdzie podany jest email

    response_data = response.get_json() #wyciągamy do zmiennej (response_data) informacje json z obiektu response
    
    
    #sprawdzamy czy  kod odpowiedzi to 409 (conflict data)
    assert response.status_code == 409
    #sprawdzamy czy content type jest ustawiony na application/json
    assert response.headers['Content-Type'] == 'application/json' 
    #sprawdzamy czy success jest False
    assert response_data['success'] is False
    #sprawdzamy czy token nie został już wysłany do clienta
    assert 'token' not in response_data



#test sprawdzający funkcje get current user
def test_get_current_user(client, user, token):
    response = client.get('/api/v1/auth/me',
                        headers={
                            'Authorization': f'Bearer {token}'
                        })#headers pozwalana na ustawienie authorization na token

    response_data = response.get_json() #wyciągamy do zmiennej (response_data) informacje json z obiektu response
    
    #sprawdzamy czy  kod odpowiedzi to 200 (ok)
    assert response.status_code == 200 
    #sprawdzamy czy content type jest ustawiony na application/json
    assert response.headers['Content-Type'] == 'application/json' 
    #sprawdzamy zawartość w body repsonse
    assert response_data['success'] is True
    #sprawdzamy czy informacje w kluczu data w body response(funkcja get_current_user ma takie pole) są identyczne jak te z fixture user
    assert response_data['data']['username'] == user['username']
    #sprawdzamy czy informacje w kluczu data w body response (funkcja get_current_user ma takie pole) są identyczne jak te z fixture user
    assert response_data['data']['email'] == user['email']
    #sprawdzamy czy informacje w kluczu data w body response sa informacje o id
    assert 'id' in response_data['data']
    #sprawdzamy czy informacje w kluczu data w body response sa informacje o creation_date
    assert 'creation_date' in response_data['data']


#test sprawdzający funkcje get current user, gdy nie podano tokena kod 401
def test_get_current_user_missing_token(client):
    response = client.get('/api/v1/auth/me')

    response_data = response.get_json() #wyciągamy do zmiennej (response_data) informacje json z obiektu response
    
    #sprawdzamy czy  kod odpowiedzi to 401 (unauthorized)
    assert response.status_code == 401 
    #sprawdzamy czy content type jest ustawiony na application/json
    assert response.headers['Content-Type'] == 'application/json' 
    #sprawdzamy zawartość w body repsonse
    assert response_data['success'] is False
    #sprawdzamy czy w body response nie ma klucza data
    assert 'data' not in response_data
