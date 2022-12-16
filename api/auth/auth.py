from webargs.flaskparser import use_args
from flask import abort, jsonify
import jwt

from api import db
from api.auth import auth_bp
from api.uti import validate_json, token_required
from api.models import User, user_schema, UserSchema, user_password_update_schema


#funkcja odpowiedzialna za rejestrowanie użytkowników
@auth_bp.route('/register', methods = ['POST']) 
@validate_json # sprawdza czy dane są w json
@use_args (user_schema, error_status_code=400)# do walidacji przesłanych danych poprzez odpowiedni schema, 400 bad request złe dane wpisane
def register(args: dict): # args to przesłane dane w zapytaniu http w body w postman, są one zwalidowane za pomocą @use_args
    
    #sprawdzenie czy nie ma takie użytkownika z taką nazwą (unique w clasie User w models.py)
    if User.query.filter(User.username == args['username']).first():#jeżeli username w bazie danych zgadza sie z przesłanym w zapytaniu username
        abort(409, description=f'User with username {args["username"]} already exists')

    #sprawdzenie czy nie ma takie użytkownika z takim emailem (unique w clasie User w models.py)
    if User.query.filter(User.email == args['email']).first():#jeżeli email w bazie danych zgadza sie z przesłanym w zapytaniu email
        abort(409, description=f'User with email {args["email"]} already exists')
    
    #w zapytaniu http będzie odkryte hasło użytkownika do bazy chcemy żeby trafiło zahashowane 
    # w clasie user tworze metodę generate_hashed_password
    args['password'] =  User.generate_hashed_password(args['password'])#zmiana passwoard za zashaowane, podmiana w słowniku args

    user = User(**args)#stworzenie użytkownika w oparciu o dane z http(słownik args)

    db.session.add(user)#dodanie do bazy danych
    db.session.commit()
    
    token = user.generate_jwt()

    return jsonify({
        'success': True,
        'token': token
    }), 201
   



    # return jsonify({
    #     'success':True,
    #     'token':token.decode()
    # })
    # #decode() przekonwertowanie bytes na string


#funkcja odpowiedzialna za logowanie użytkowników
@auth_bp.route('/login', methods = ['POST']) 
@validate_json # sprawdza czy dane są w json
@use_args (UserSchema(only=['username', 'password']), error_status_code=400)#sprawdzamy czy klient wysłał nazwę użytkownika i hasło
def login(args: dict): # args to przesłane dane w zapytaniu http w body w postman, są one zwalidowane za pomocą @use_args
    user = User.query.filter(User.username == args['username']).first() # wyciągamy login o podanej nazwie użytkownika
    if not user: #jeżeli użytkownik o takim username nie istnieje
        abort(401, description=f'invalid credentials')#nieprawidłowe dane uwierzytelniające

    #sprawdzamy czy podane hasło jest zgodne z tym które istnieje w bd dla tego użytkownika
    if not user.is_password_valid(args['password']):#klucz ze słownika to wpisane przez klienta hasło
        abort(401, description=f'invalid credentials')#nieprawidłowe dane uwierzytelniające


    token = user.generate_jwt()#wygenerowanie tokena

    return jsonify({
        'success': True,
        'token': token
    })#decode() przekonwertowanie bytes na string




@auth_bp.route('/me', methods= ['GET'])
@token_required
def get_current_user(user_id:int):
    user = User.query.get_or_404(user_id, description = 'User with id {user_id} not found')#wyciągniecie usera na podstawie user_id z request

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)
    })

   
@auth_bp.route('/update/password', methods= ['PUT'])
@token_required
@validate_json
@use_args(user_password_update_schema, error_status_code=400)#walidacja danych przez schema do current i new password
def update_user_password(user_id:int, args:dict):
    user = User.query.get_or_404(user_id, description = 'User with id {user_id} not found')#wyciągniecie usera na podstawie user_id z request

    #sprawdzam za pomocą funkcji z classy User is_password valid czy current_password jest poprawne
    if not user.is_password_valid(args['current_password']):
        abort(401, description='Invalid password')# 401 unauthorized


    #jeżeli current_password jest poprawne to możemy je zmienić na new_password
    user.password = user.generate_hashed_password(args['new_password'])#hashujemy new_password


    db.session.commit()#zapisanie zmian do bd

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)
    })




@auth_bp.route('/update/data', methods= ['PUT'])
@token_required
@validate_json
@use_args(UserSchema(only=['username', 'email']), error_status_code=400)#walidacja danych przez schema tylko do 2 danych username i email
def update_user_data(user_id:int, args:dict):

    #username i email są unikalne dlatego muszę sprawdzić czy nazwa lub email nie są używane przez innego użytkownika
    
    #sprawdzenie czy nie ma takie użytkownika z taką nazwą (unique w clasie User w models.py)
    if User.query.filter(User.username == args['username']).first():#jeżeli username w bazie danych zgadza sie z przesłanym w zapytaniu username
        abort(409, description=f'User with username {args["username"]} already exists')

    #sprawdzenie czy nie ma takie użytkownika z takim emailem (unique w clasie User w models.py)
    if User.query.filter(User.email == args['email']).first():#jeżeli email w bazie danych zgadza sie z przesłanym w zapytaniu email
        abort(409, description=f'User with email {args["email"]} already exists')

    #wyciągniecie użytkownika z bazy danych o podanym user_id
    user = User.query.get_or_404(user_id, description = 'User with id {user_id} not found')#wyciągniecie usera na podstawie user_id z request

    #jeżeli istnieje taki user to mogę zmienic username i email dla tego użytkownika
    user.username = args['username']#args to wprowadzone dane w body w postman
    user.email = args['email']

    db.session.commit()#zapisanie zmian do bd

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)
    })
