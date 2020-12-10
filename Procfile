web: gunicorn main.wsgi
worker: celery -A main worker --beat -S django --l info
