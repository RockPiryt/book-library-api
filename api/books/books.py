from flask import jsonify, abort #abort do update book

from api import db
from api.books import books_bp
from api.models import Book, BookSchema, book_schema, Author, validates
from api.uti import get_schema_args, apply_order, apply_filter, get_pagination, token_required

# do funkcji update book
from api.uti import validate_json
from webargs.flaskparser import use_args



@books_bp.route('/books', methods = ['GET'])
def get_books():
    query = Book.query#zapytanie do bazy danych w zmiennej
    schema_args = get_schema_args(Book)# przesłanie klasy Book jako model do funkcji w uti.py
    query = apply_order(Book, query)#dodanie metody odpowiedzialnej za sortowanie, pierwszy parametr to query, drugi to sort w params w postman
    query = apply_filter(Book, query)# obiekt query z funkcją filtrowania, nie podaje konkretnie args, bo można wpisać wszystko
    items, pagination = get_pagination(query, 'booksblue.get_books') #wypakowanie krotki Tuple z funkcji get_pagination, w zmiennej items są informacje o books dlatego nie potrzebna kolejna linijka
    books = BookSchema(**schema_args).dump(items)

 
    return jsonify({
            'success': True,
            'data': books,
            'number_of_records': len(books),
            'pagination': pagination

        })





@books_bp.route('/books/<int:book_id>', methods = ['GET']) 
def get_book(book_id:int):
    book = Book.query.get_or_404(book_id, description =f'Book with id {book_id} not found' )

    return jsonify({
            'success': True,
            'data':book_schema.dump(book)
        })





@books_bp.route('/books/<int:book_id>', methods = ['PUT']) 
@token_required
@validate_json # sprawdza czy dane są w json
@use_args (book_schema, error_status_code=400)# do walidacji przesłanych danych poprzez odpowiedni schema, 400 bad request złe dane wpisane
def update_book(user_id:int, args: dict, book_id:int): # args to przesłane dane w zapytaniu http w body w postman, są one zwalidowane za pomocą @use_args
    book = Book.query.get_or_404(book_id, description =f'Book with id {book_id} not found' ) #sprawdzamy czy dany rekord z książką istenieje w bd
    #sprawdzenie czy książka z takim isbn jest  już w bazie danych
    # nie możemy zrobić update książki z rekordem 5 (z isbn przesłanym jak dla ksiązki z id 4 ), bo byłyby 2 ksiązki z takim samym isbn
    if Book.query.filter(Book.isbn == args['isbn']).first():#jeżeli isbn w bazie danych zgadza sie z przesłanym w zapytaniu isbn
        abort(409, description=f'Book with ISBN {args["isbn"]} already exists')

    book.title = args['title']
    book.isbn = args['isbn']
    book.number_of_pages = args['number_of_pages']

    #description oraz author id to pola opcjonalne
    description = args.get('description') #jeżeli zostało coś wpisane w polu description
    if description is not None:
        book.description = description

    author_id = args.get('author_id') #jeżeli zostało coś wpisane w polu author_id
    if author_id is not None:
        Author.query.get_or_404(author_id, description =f'Author with id {author_id} not found' )#sprawdzam czy author_id jest w bazie danych
        book.author_id = author_id

    db.session.commit()

    return jsonify({
            'success': True,
            'data':book_schema.dump(book)
        })


@books_bp.route('/books/<int:book_id>', methods = ['DELETE'])
@token_required
def delete_book(user_id:int, book_id:int):
    book = Book.query.get_or_404(book_id, description =f'Book with id {book_id} not found' )#wyciągnięcie book z db 
    db.session.delete(book)
    db.session.commit()

    return jsonify({
            'success': True,
            'data':f'Book with id {book_id} has been deleted'
        })

@books_bp.route('/authors/<int:author_id>/books', methods = ['GET'])
def get_all_author_books(author_id: int):
     Author.query.get_or_404(author_id, description =f'Author with id {author_id} not found' )#sprawdzenie czy taki autor jest w bd
     #wyciągniecie ksiązek dla autora o podanym id
     books = Book.query.filter(Book.author_id == author_id).all()

     items = BookSchema(many=True, exclude=['author']).dump(books)#bookSchema -serializacja danych, nie chcemy dostawać szegółowych info o autorze
     
     return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
        })

@books_bp.route('/authors/<int:author_id>/books', methods = ['POST'])
@token_required
@validate_json
@use_args(BookSchema(exclude=['author_id']), error_status_code=400) #wykluczamy author_id bo jest w przesyłanym adresie URL
def create_book(user_id:int, args:dict, author_id: int):
    Author.query.get_or_404(author_id, description =f'Author with id {author_id} not found' )#sprawdzenie czy taki autor jest w bd
    if Book.query.filter(Book.isbn == args['isbn']).first(): #sprawdzenie czy nie ma już książki z takim isbn
        abort(409, description=f'Book with ISBN {args["isbn"]} already exists')

    book = Book(author_id = author_id, **args)#wypakowanie słownika args oraz przekazenie jako argument author_id który jest w URL
    db.session.add(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': book_schema.dump(book)
        }),201 #kod 201 czyli created

