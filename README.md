# Book Library REST API
REST API for online library.
The documentation can be found https://documenter.getpostman.com/view/24234549/2s8YzXw117

# Setup

- Clone repository
- Create  database and user
- Rename .env.example to .env and set your calues

```buildoutcfg
# SQLALCHEMY_DATABASE_URI template
SQLALCHEMY_DATABASE_URI = mysql+pymysql://{db_user}:{db_password}@{db_host}/{database}?charset=utf8mb4
```

- Create a virtual evironment
```buildoutcfg
python -m venv venv
```

- Install packages from requirements.txt
```buildoutcfg
pip install -r requirements.txt
```

- Migrate database
```buildoutcfg
flask db upgrade
```

- Run command
```buildoutcfg
flask run
```

# Note
Import/delete example data from
```
api/samples
```

```
# import
flask db-manage add-data

# remove
flask db-manage remove-data
```

# Tests
In order to execute tests located in tests/ run the command
```
python -m pytest tests/
```

# Technologies / Tools
- Python 3.11
- Flask 2.2.2
- Alembic 1.8.1
- SQLAlchemy 1.4.43
- Pytest 7.2.0
- MySQL
- AWS
- Postman


alembic==1.8.1
attrs==22.1.0
autopep8==2.0.0
cffi==1.15.1
click==8.1.3
colorama==0.4.6
cryptography==38.0.3
Flask==2.2.2
Flask-Migrate==3.1.0
Flask-SQLAlchemy==3.0.2
greenlet==2.0.1
iniconfig==1.1.1
itsdangerous==2.1.2
Jinja2==3.1.2
Mako==1.2.3
MarkupSafe==2.1.1
marshmallow==3.19.0
packaging==21.3
pathlib==1.0.1
pluggy==1.0.0
pycodestyle==2.10.0
pycparser==2.21
PyJWT==2.6.0
PyMySQL==1.0.2
pyparsing==3.0.9
pytest==7.2.0
python-dotenv==0.21.0
SQLAlchemy==1.4.43
tomli==2.0.1
webargs==8.2.0
Werkzeug==2.2.2

