from api import create_app
#create_app to funkcja z pliku init.py

application = create_app('production')#stworzenie aplikacji w oparciu o  konfigurację produkcyjną z pliku config.py