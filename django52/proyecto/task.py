from celery import shared_task
import time

@shared_task
def tarea_lenta():
    print("iniciando tarea...")
    time.sleep(5)
    print("tarea finalizada")