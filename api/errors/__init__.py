from flask import Blueprint

errors_bp = Blueprint('errorsblue', __name__)

from api.errors import errors