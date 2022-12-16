from api import create_app #import def create app, która tworzy nowe instancje klasy app

app = create_app() #stworzenie instancji klasy flask=app



if __name__ == '__main__':# można skasować jak wykorzystamy plik .flaskenv - lekcja 24
    app.run()

