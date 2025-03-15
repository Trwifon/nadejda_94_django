Create a project nadejda_94_django with venv
If you have pycharm pro create django project
pip install django
git config --global github.user Trwifon
git clone https://github.com/Trwifon/nadejda_94_django.git
put .env and .ignore in manage.py directory
in .env or settings.py setup db and allowed hosts
pip install -r requirements.txt
python manage.py runserver 'myhost':8000


get last version to server

git pull origin master
git stash
git pull origin master
:qa
python manage.py migrate
