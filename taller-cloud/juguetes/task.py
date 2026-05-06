import time
import logging
from celery import shared_task
from .models import Juguete

logger = logging.getLogger(__name__) #se configura el logger para que muestre mensajes en la consola

@shared_task
def calcular_valor_inventario():
#Tarea pesada 1 donde se calcula el valor total del inventario digamos
#aqui simula procesamiento de 10 segundos
    logger.info("Iniciando calculo de valor de inventario...")
    time.sleep(10)
    juguetes = Juguete.objects.all() #se obtiene todos los juguetes de la base de datos
    
    total_valor = sum(j.precio * j.stock for j in juguetes) #se calcula el valor total del inventario multiplicando el precio por el stock de cada juguete y sumando todo
    
    resultado = {
        'total_juguetes': juguetes.count(),
        'valor_total_inventario': float(total_valor),
        'moneda': 'CLP'
    }
    
    logger.info(f"Calculo completo: {resultado}")
    return resultado

@shared_task
def enviar_alerta_stock_bajo(minimo_stock=5):
    #tarea pesada 2: donde se verifica stock bajo y envia alertas
    #aqui simula procesamiento de 8 segundos
    logger.info(f"Verificando productos con stock menor a {minimo_stock}...")
    
    time.sleep(8) ##simula envio de emails
    
    productos_bajos = Juguete.objects.filter(stock__lt=minimo_stock) #se filtra los juguetes que tienen stock menor al minimo
    
    resultado = {
        'alertas_enviadas': productos_bajos.count(),
        'productos_afectados': list(productos_bajos.values('nombre', 'stock')),
        'mensaje': f'Se enviaron alertas para {productos_bajos.count()} productos'
    }
    logger.info(f"Alertas generadas: {resultado}")
    return resultado


@shared_task
def procesar_venta_asinc(juguete_id, cantidad, cliente_email):
    #tarea que procesa una venta de forma asincrona
    #aqui simula facturacion y email
    
    logger.info(f"Procesando venta de {cantidad} unidades del producto {juguete_id}")
    time.sleep(5) #simula procesamiento de venta y envio de email
    
    #simular actualizaciion de stock
    try:
        juguete = Juguete.objects.get(id=juguete_id)
        
        #verifica que hay stock disponible
        if juguete.stock < cantidad:
            logger.warning(f"stock insuficiente para {juguete.nombre}")
            return {
                'estado': 'error',
                'mensaje': f'Stock insuficiente. Disponible: {juguete.stock}, Solicitado: {cantidad}',
                'producto': juguete.nombre
            }
        #actualiza el stock
        juguete.stock -= cantidad
        juguete.save()
        
        nuevo_stock = juguete.stock
        total_venta = juguete.precio * cantidad
        #se crea mensaje de confirmacion
        mensaje = f"""
Hola,
Tu compra ha sido procesada exitosamente:
Producto: {juguete.nombre}
Cantidad: {cantidad} unidades
Precio Unitario: ${juguete.precio}
Total: ${total_venta}

Stock restante en tienda: {nuevo_stock} unidades

Gracias por tu compra!
"""
        #envia correo de confirmacion simulado
        
        logger.info(f"Enviando email de confirmacion a {cliente_email}...")
        time.sleep(2) #simula envio de email
        logger.info("Email enviado exitosamente")
        resultado = {
            'estado': 'completado',
            'producto': juguete.nombre,
            'cantidad': cantidad,
            'precio_unitario': float(juguete.precio),
            'total_venta': float(total_venta),
            'stock_anterior': juguete.stock + cantidad,
            'stock_restante': nuevo_stock,
            'email_enviado': cliente_email,
        }
        logger.info(f"Venta completada: {resultado}")
        return resultado
        
            
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        return {
            'estado': 'error',
            'mensaje': f'Error al procesar venta: {str(e)}'
        }