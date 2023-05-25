python -m venv dpienv
goto env
 pip install -r requirements.txt
 python.exe -m pip install --upgrade pip
 
django-admin startproject watchmate .
python manage.py startapp watchlist_app
python manage.py runserver 8000

python manage.py makemigrations 
python manage.py migrate