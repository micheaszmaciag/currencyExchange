import os
from celery import Celery

# Sets up the Celery application for the currencyExchange project.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'currencyExchange.settings')

app = Celery('currencyExchange')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()