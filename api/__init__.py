from flask import Flask
from config import config #zmiana clasy ogólnej Config na zmienną config (słownik z 2 kluczami)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#app = Flask(__name__)
#app.config.from_object(Config)

db = SQLAlchemy() #obiekt globalny, usuwam app bo jest tworzona w metodzie create_app
migrate = Migrate() #obiekt globalny,usuwam app i db bo jest tworzona w metodzie create_app

#def create_app(config_class=Config): zmiany klasy na nazwę kofiguracji
def create_app(config_name='development'): # defaltowo ustawiamy parametr config_class na Config z pliku config.py
    app = Flask(__name__) #tworzę obiekt app
    app.config.from_object(config[config_name]) #pobranie konfiguracji

    #powiązanie app z globalnymi obiektami db i migrate
    db.init_app(app)
    migrate.init_app(app, db)

    #import bluprintów z katalagów
    from api.authors import authors_bp
    from api.errors import errors_bp
    from api.commands import db_manage_cmd_bp
    from api.books import books_bp
    from api.auth import auth_bp

    #powiązanie zaimportowanych bluprintów z aplikacją  
    app.register_blueprint(authors_bp, url_prefix='/api/v1')#url_prefix to wartość dodana do każdego url wewnątrz bluprintu authors
    app.register_blueprint(errors_bp)
    app.register_blueprint(db_manage_cmd_bp)
    app.register_blueprint(books_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

    return app



#import api.authors
#import api.models
#import api.commands.db_manage_commands
#import api.errors


#@app.route('/') 
#def index(): 
    #db.create_all() 
     
    #return '''Hello Flask-SQLAlchemy''' 
