from django.db import models

# Create your models here.
class Juguete(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del juguete")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.IntegerField(verbose_name="Stock disponible")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Juguete"
        verbose_name_plural = "Juguetes"
#verbose_name es la etiqueta legible "Nombre del juguete"
#blank=true es para marcar tipo que el campo es opcional
#aauto_now_add es para que se guarde la fecha de creacion del jueguete automaticament
# al momento de crear el registro en la base de datos
