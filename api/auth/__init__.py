from flask import Blueprint

auth_bp =  Blueprint('authblue', __name__)

from api.auth import auth