from flask import Flask


def test_app(app): #przekazyjemy app z pliku conftest z liniki yield app (jest to pytest.fixture)
#sprawdzamy czy app jest instancją klasy Flask
    assert isinstance (app, Flask) # app to wynik z yield
#sprawdzamy czy app ma odpowiednią konfiguracje
    assert app.config['TESTING'] is True
#sprawdzamy czy app ma ustawiony debug
    assert app.config['DEBUG'] is True