from flask import Blueprint # import obiektu Blueprint

authors_bp = Blueprint('authorsblue', __name__)#1 argument to nazwa blueprint, 2 argument to nazwa pakietu, standardowo __name__

from api.authors import authors