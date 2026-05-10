.PHONY: run migrate migrations shell check-env install freeze

run:
	python manage.py runserver

migrate:
	python manage.py migrate

migrations:
	python manage.py makemigrations

shell:
	python manage.py shell

check-env:
	python manage.py check_env

install:
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt