import time
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import Juguete
from .task import calcular_valor_inventario, enviar_alerta_stock_bajo, procesar_venta_asinc
#parte sincronica
def lista_juguetes(request):
    #Lista todos los juguetes (sincrono - rápido)
    juguetes = Juguete.objects.all()
    return render(request, 'juguetes/lista.html', {'juguetes': juguetes})

def detalle_juguete(request, id):
    #Ver detalle de un juguete (sincrono)
    juguete = get_object_or_404(Juguete, id=id)
    return render(request, 'juguetes/detalle.html', {'juguete': juguete})

def crear_juguete(request):
    #Crear nuevo juguete (sincrono)
    if request.method == 'POST':
        
        #validamos precio
        try:
            precio = float(request.POST.get('precio', 0))
            if precio < 0:
                return render(request, 'juguetes/form.html', {
                    'error': 'El precio no puede ser negativo'
                }
                )
        except ValueError:
            return render(request, 'juguetes/form.html', {
                'error': 'El precio debe ser un numero valido'
            })
        #validamos stock
        try:
            stock = int(request.POST.get('stock', 0))
            if stock < 0:
                return render(request, 'juguetes/form.html', {
                    'error': 'El stock no puede ser negativo'
                })
        except ValueError:
            return render(request, 'juguetes/form.html', {
                'error': 'El stock debe ser un numero entero valido'
            })
        #validamos nombre si ta vacio
        nombre = request.POST.get('nombre', '').strip()
        if not nombre:
            return render(request, 'juguetes/form.html', {
                'error': 'El nombre del juguete no puede estar vacio'
            })
        
        
        juguete = Juguete.objects.create(
            nombre=request.POST.get('nombre'),
            precio=request.POST.get('precio'),
            stock=request.POST.get('stock'),
            descripcion=request.POST.get('descripcion', '')
        )
        return redirect('lista_juguetes')
    return render(request, 'juguetes/form.html')

def editar_juguete(request, id):
    #Editar juguete (sincrono)
    juguete = get_object_or_404(Juguete, id=id)
    if request.method == 'POST':
        juguete.nombre = request.POST.get('nombre')
        juguete.precio = request.POST.get('precio')
        juguete.stock = request.POST.get('stock')
        juguete.descripcion = request.POST.get('descripcion', '')
        juguete.save()
        return redirect('lista_juguetes')
    return render(request, 'juguetes/form.html', {'juguete': juguete})

def eliminar_juguete(request, id):
    #eliminar juguete (sincrono)
    juguete = get_object_or_404(Juguete, id=id)
    if request.method == 'POST':
        juguete.delete()
        return redirect('lista_juguetes')
    return render(request, 'juguetes/confirmar_eliminar.html', {'juguete': juguete})


#parte asincronica
def reporte_inventario_asinc(request):
    #endpoint asincrono 1
    #responde inmediato, el worker procesa en segundo plano
    
    tarea = calcular_valor_inventario.delay()
    return JsonResponse({
        'task_id': tarea.id,
        'estado': 'procesando_en_segundo_plano',
        'mensaje': 'El reporte se está generando. Recibirás notificación cuando termine.',
        'tiempo_estimado': '10 segundos'
    })

def alerta_stock_asinc(request):
    #endpoint asincrono 2
    #responde inmediato, el worker procesa en segundo plano
    tarea = enviar_alerta_stock_bajo.delay(5)
    return JsonResponse({
        'task_id': tarea.id,
        'estado': 'procesando_en_segundo_plano',
        'mensaje': 'Verificando inventario y enviando alertas...',
        'tiempo_estimado': '8 segundos'
    })

@csrf_exempt
@require_http_methods(["POST"])
def procesar_compra(request):
    """Procesa compra de forma SÍNCRONA - actualiza stock inmediatamente"""
    try:
        data = json.loads(request.body)
        juguete_id = data.get('juguete_id')
        cantidad = int(data.get('cantidad', 1))
        cliente_email = data.get('cliente_email', 'cliente@ejemplo.com')
        
        # Obtén el juguete
        juguete = get_object_or_404(Juguete, id=juguete_id)
        
        # Verifica stock
        if juguete.stock < cantidad:
            return JsonResponse({
                'estado': 'error',
                'mensaje': f'❌ Stock insuficiente. Disponible: {juguete.stock}, Solicitado: {cantidad}',
                'producto': juguete.nombre
            }, status=400)
        
        # Actualiza stock INMEDIATAMENTE
        juguete.stock -= cantidad
        juguete.save()
        
        time.sleep(8)
        
        nuevo_stock = juguete.stock
        total_venta = float(juguete.precio) * cantidad
        
        # Crea mensaje de confirmación
        mensaje_confirmacion = f"""Hola,

Tu compra ha sido procesada exitosamente:

Producto: {juguete.nombre}
Cantidad: {cantidad} unidades
Precio Unitario: ${juguete.precio}
Total: ${total_venta}

Stock restante en tienda: {nuevo_stock} unidades

¡Gracias por tu compra!"""
        
        # Log para ver en consola
        print(f"\n{'='*60}")
        print(f"✅ VENTA PROCESADA")
        print(f"{'='*60}")
        print(mensaje_confirmacion)
        print(f"{'='*60}\n")
        
        return JsonResponse({
            'estado': 'completado',
            'producto': juguete.nombre,
            'cantidad': cantidad,
            'precio_unitario': float(juguete.precio),
            'total_venta': total_venta,
            'stock_anterior': juguete.stock + cantidad,
            'stock_restante': nuevo_stock,
            'email_enviado': cliente_email,
            'mensaje': mensaje_confirmacion
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'estado': 'error'}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def procesar_compra_asinc(request):
    #endpoint asincrono 3
    #responde inmediato, el worker procesa en segundo plano
    try:
        data = json.loads(request.body)
        juguete_id = data.get('juguete_id')
        cantidad = data.get('cantidad', 1)
        cliente_email = data.get('cliente_email', 'cliente@ejemplo.com')
        
        tarea = procesar_venta_asinc.delay(juguete_id, cantidad, cliente_email)
        
        return JsonResponse({
            'task_id': tarea.id,
            'estado': 'compra_recibida',
            'mensaje': '¡Compra realizada con éxito! Recibirás confirmación por email.',
            'tiempo_estimado': '15 segundos'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
def verificar_estado_tarea(request, task_id):
    #endpoint para verificar el estado de una tarea
    from celery.result import AsyncResult
    from proyecto.celery import app
    
    resultado = AsyncResult(task_id, app=app)
    
    if resultado.ready():
        return JsonResponse({
            'task_id': task_id,
            'estado': 'completado',
            'resultado': resultado.result
        })
    else:
        return JsonResponse({
            'task_id': task_id,
            'estado': 'pendiente',
            'mensaje': 'La tarea aún está procesándose'
        })