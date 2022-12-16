import os
from dotenv import load_dotenv # do obsługi pliku env
from pathlib import Path 

base_dir = Path(__file__).resolve().parent#base_dir to sieżka podstawowa
env_file = base_dir / '.env'#lokalizacja pliku env w  base_dir
#print(env_file)#pojawiają sie w konsoli ustawienia w env
load_dotenv(env_file) #załaduj plik env


#configuracja z której korzysta środowisko developerskie
class Config:
    SECRET_KEY= os.environ.get('SECRET_KEY')# wyciąganie danych ze zmiennych środowiskowych w pliku .env
    SQLALCHEMY_DATABASE_URI= '' # pusty string oznacza że uri musi być nadpisane przez clasy pochodne DevelopmentConfig lub TestingConfig
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PER_PAGE = 5
    JWT_EXPIRED_MINUTES = 30

#print(Config.SECRET_KEY)#pojawiają sie w konsoli ustawienia w env
#print(Config.SQLALCHEMY_DATABASE_URI)#pojawiają sie w konsoli ustawienia w env


#configuracja dla środowiska developerskiego - baza danych MYSQL (działa na serwerze)
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI= os.environ.get('SQLALCHEMY_DATABASE_URI')# wyciąganie wartości ze zmiennych środowiskowych w pliku .env
    #SQLALCHEMY_DATABASE_URI= 'mysql+pymysql://book_lib_user:dbhaslo1@book-library-db.cydmitb0qsmy.eu-west-1.rds.amazonaws.com/book-library-db?charset=utf8mb4'


#configuracja dla środowiska testowego - baza danych SQLite (działa na plikach)
class TestingConfig(Config):
    DB_FILE_PATH = base_dir / 'tests' / 'test.db' #ścieżka do pliku sqlite, base_dir jest obiektem PATH z pakietu Pathlib
    SQLALCHEMY_DATABASE_URI= f'sqlite:///{DB_FILE_PATH}'
    #SQLALCHEMY_DATABASE_URI= 'sqlite:///<file_path>'#ogólna ścieżka do pliku sqlite
    DEBUG = True
    TESTING = True # infromuje aplikacje flaskową że działamy w trybie testowania


#configuracja dla środowiska produkcyjnego - baza danych RDS - do wdrożenia na AWS, przechowuje dane do bd na AWS
class ProductionConfig(Config):
    DB_HOST = os.environ.get('DB_HOST')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')
    SQLALCHEMY_DATABASE_URI = F'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4'

#tworzymy słownik który będzie przechowywał konfigurację testową i deweloperską
#zmienna config w zależności od przekazanego do niej klucza 'development'/'testing' będzie zwracała odpowiednią konfiguracje dla specyficznego środowiska
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
