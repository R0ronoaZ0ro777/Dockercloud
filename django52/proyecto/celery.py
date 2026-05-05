import os
from celery import Celery

#se define la variable de entorno para el modulo configuracion de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto.settings')

#se crea una instancia de celery con el nombre del proyecto
app = Celery('proyecto')

#se configura celery para que lea las configuraciones desde el modulo de configuaracion django

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()