import pytest

#sprawdzamy czy serwer zwróci poprawne dane jak nie ma jeszcze danych w bd
def test_get_authors_no_records(client):
    response = client.get('/api/v1/authors')#wysłanie zapytania GET
    #oczekiwane wartości z pliku authors.py funkcja get_authors
    #current page to adres url z podaniem strony 
    # dane do pagination z uti.py
    expected_result ={
        'success': True,
        'data': [],
        'number_of_records': 0,
        'pagination': {
            'total_pages': 0,
            'total_records': 0,
            'current_page': '/api/v1/authors?page=1'
                    }
        }

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.get_json() == expected_result # sprawddzam czy body response (dane w json) są zgodne z expected result


#test funkcji z danymi z pliku sample_data
def test_get_authors(client, sample_data):
    response = client.get('/api/v1/authors')#wysłanie zapytania GET
    response_data = response.get_json() #zmienna przechowywująca dane json z body repsonse 

    assert response.status_code == 200 #200 ok
    assert response.headers['Content-Type'] == 'application/json'

    assert response_data['success'] is True
    assert response_data['number_of_records'] == 5 #tak mamy ustawione w paginacji
    assert len(response_data['data']) == 5 #sprawdzamy ilość elementów w liście data, czyli 5 recordów na strone
    assert response_data['pagination'] == {
        'total_pages': 2,
        'total_records': 10,
        'current_page': '/api/v1/authors?page=1',
        'next_page': '/api/v1/authors?page=2',
                }



#test funkcji z dodatkowymi params w zapytaniu GET
def test_get_authors_with_params(client, sample_data):
    response = client.get('/api/v1/authors?fields=name&sort=-id&page=2&limit=2')#wysłanie zapytania GET z params
    response_data = response.get_json() #zmienna przechowywująca dane json z body repsonse 

    assert response.status_code == 200 #200 ok
    assert response.headers['Content-Type'] == 'application/json'

    assert response_data['success'] is True
    assert response_data['number_of_records'] == 2 #tak mamy ustawione w paginacji
    assert response_data['pagination'] == {
        'total_pages': 5,
        'total_records': 10,
        'current_page': '/api/v1/authors?page=2&fields=name&sort=-id&limit=2',
        'next_page': '/api/v1/authors?page=3&fields=name&sort=-id&limit=2',
        'previous_page': '/api/v1/authors?page=1&fields=name&sort=-id&limit=2'
                }
    assert response_data['data'] == [
        {'name':'Alice'},
        {'name':'Dan'}
    ]
    #oczekujemy listy z 2 elementami, słownikami -- imiona z pliku sample_data nie ode mnie z aplikacji bo tam mam 12 rekordów


#test funkcji  get_author(pojedyńczy autor)z danymi z pliku sample_data
def test_get_single_author(client, sample_data):
    response = client.get('/api/v1/authors/9')#wysłanie zapytania GET z podaniem nr id
    response_data = response.get_json() #zmienna przechowywująca dane json z body repsonse 

    assert response.status_code == 200 #200 ok
    assert response.headers['Content-Type'] == 'application/json'

    assert response_data['success'] is True
    assert response_data['data']['name'] == 'Andrzej' #sprawdzamy imie dla rekordu 9 podanego w url
    assert response_data['data']['last'] == 'Sapkowski' #sprawdzamy nazwisko dla rekordu 9 podanego w url
    assert response_data['data']['birth_date'] == '21-06-1948' #sprawdzamy nazwisko dla rekordu 9 podanego w url
    assert len(response_data['data']['books']) == 1 #sprawdzamy ilość książek sapkowskiego


#test funkcji  get_author(pojedyńczy autor) czy wyświetli kod 404 jak utora nie ma w bd
def test_get_single_author_not_found(client):
    response = client.get('/api/v1/authors/30')#wysłanie zapytania GET z podaniem nr id
    response_data = response.get_json() #zmienna przechowywująca dane json z body repsonse 

    assert response.status_code == 404 #not found
    assert response.headers['Content-Type'] == 'application/json'

    assert response_data['success'] is False
    assert 'data' not in response_data #sprawdzamy czy bedzie brakowało klucza data w body response


#test funkcji  create_author
def test_create_author(client, token, author):
    response = client.post('/api/v1/authors',
                            json=author,
                            headers={
                                'Authorization': f'Bearer {token}'
                            }
    
    )#wysłanie zapytania POST z danymi z author oraz z tokenem
    response_data = response.get_json() #zmienna przechowywująca dane json z body repsonse 

    expected_result = {
        'success':True,
        'data':{
            **author,
            'id': 1,
            'books':[]
        }
    }#oczekiwane wartości w body response, w books będzie domyślnie 0 ksiązek

    assert response.status_code == 201 #created
    assert response.headers['Content-Type'] == 'application/json'

    assert response_data == expected_result

    #sprawdzenie czy taki record 1 został utworzony w bd
    response = client.get('/api/v1/authors/1')#wysłanie zapytania GET z podaniem nr id
    response_data = response.get_json() #zmienna przechowywująca dane json z body repsonse 

    assert response.status_code == 200 #200 ok
    assert response.headers['Content-Type'] == 'application/json'

    assert response_data == expected_result


#test funkcji  create_author - scenariusze negatywne
#funkcja sprawdzjaca czy klient zawarł wszystkie dane w body zapytania http

@pytest.mark.parametrize(
    'data, missing_field',
    [   ({'last': 'Mickiewicz', 'birth_date': '24-12-1798'},'name'),
        ({'name': 'Adam', 'birth_date': '24-12-1798'},'last'),
        ({'name': 'Adam', 'last': 'Mickiewicz'},'birth_date')
    ]
    ) 
def test_create_author_invalid_data(client, token, data, missing_field):
    response = client.post('/api/v1/authors',
                            json=data,
                            headers={
                                'Authorization': f'Bearer {token}'}
                            )


    #wyciągamy dane zapisane w ciele odpowiedzi (body respone) z serwera
    response_data = response.get_json() #wyciągamy do zmiennej (response_data) informacje json z obiektu response
    
    
    #sprawdzamy czy  kod odpowiedzi to 400 (bad request)
    assert response.status_code == 400
    #sprawdzamy czy content type jest ustawiony na application/json
    assert response.headers['Content-Type'] == 'application/json' 
    #sprawdzamy zawartość w body repsonse czy jest na False w przypadku braku jakiegoś missing_field
    assert response_data['success'] is False
    #sprawdzamy nie ma data w body response
    assert 'data' not in response_data
    #sprawdzamy missing_field jest w messeage w body response tak jak w postman
    assert missing_field in response_data['message']
    #sprawdzamy czy w missing_field (w kluczu message)przechowywyuje informacje Missing data for required field.
    assert 'Missing data for required field.' in response_data['message'][missing_field]





#test funkcji  create_author, funkcja sprawdzjaca czy klient zawarł content type w nagłowku
def test_create_author_invalid_content_type(client, token, author):
    response = client.post('/api/v1/authors',
                            data=author,
                            headers={
                                'Authorization': f'Bearer {token}'}
                            )


    #wyciągamy dane zapisane w ciele odpowiedzi (body respone) z serwera
    response_data = response.get_json() #wyciągamy do zmiennej (response_data) informacje json z obiektu response
    
    
    #sprawdzamy czy  kod odpowiedzi to 415 (unsupported media)
    assert response.status_code == 415
    #sprawdzamy czy content type jest ustawiony na application/json
    assert response.headers['Content-Type'] == 'application/json' 
    #sprawdzamy nie ma data w body response
    assert 'data' not in response_data



#test funkcji  create_author, funkcja sprawdzjaca czy klient przesłał token
def test_create_author_missing_token(client, author):
    response = client.post('/api/v1/authors',
                            json=author,
                            )
    response_data = response.get_json() #wyciągamy do zmiennej (response_data) informacje json z obiektu response

    #sprawdzamy czy  kod odpowiedzi to 401 (unauthorized)
    assert response.status_code == 401
    #sprawdzamy czy content type jest ustawiony na application/json
    assert response.headers['Content-Type'] == 'application/json' 
    #sprawdzamy nie ma data w body response
    assert 'data' not in response_data