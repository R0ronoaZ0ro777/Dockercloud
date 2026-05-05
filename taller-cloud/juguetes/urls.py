from django.urls import path
from . import views

urlpatterns = [
    #vistas sincronas (CRUD)
    path('', views.lista_juguetes, name='lista_juguetes'),
    path('<int:id>/', views.detalle_juguete, name='detalle_juguete'),
    path('crear/', views.crear_juguete, name='crear_juguete'),
    path('<int:id>/editar/', views.editar_juguete, name='editar_juguete'),
    path('<int:id>/eliminar/', views.eliminar_juguete, name='eliminar_juguete'),
    
    #vistas asincronas (Celery)
    path('reporte-inventario/', views.reporte_inventario_asinc, name='reporte_inventario'),
    path('alerta-stock/', views.alerta_stock_asinc, name='alerta_stock'),
    path('procesar-compra/', views.procesar_compra_asinc, name='procesar_compra'),
    path('estado-tarea/<str:task_id>/', views.verificar_estado_tarea, name='estado_tarea'),
]