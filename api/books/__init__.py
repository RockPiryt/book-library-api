from flask import Blueprint

books_bp = Blueprint('booksblue', __name__)

from api.books import books