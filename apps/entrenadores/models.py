from django.db import models

# Create your models here.


class EntrenamientoTurno(models.Model):
    desde = models.TimeField()
    hasta = models.TimeField()

    def __str__(self):
        return f"{self.desde} - {self.hasta}"
    
    class Meta:
        ordering = ["desde",]


class DiasEntrenamiento(models.Model):
    dias = models.CharField(("Días"), max_length=50)

    def __str__(self):
        return f"{self.dias}"


class LugarEntrenamiento(models.Model):
    lugar = models.CharField(("Lugar"), max_length=50)
    cupo_entrenador = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.lugar}"

class Entrenadores(models.Model):
    nombre = models.CharField(max_length=25)
    mail = models.EmailField(null=True, blank=True)
    telefono = models.IntegerField(default=0, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    dni = models.IntegerField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=12, default='Argentina')
    observacion = models.CharField(max_length=50, null=True, blank=True)
    habilitado = models.BooleanField(default=False)
    seguro = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre}"
    
    class Meta:
        verbose_name = "Entrenador"
        verbose_name_plural = "Entrenadores"


class AsignarDiasEntrenamiento(models.Model):
    entrenador = models.ForeignKey(Entrenadores, verbose_name=(
        "Entrenador"), on_delete=models.CASCADE)
    lugar = models.ForeignKey(LugarEntrenamiento, verbose_name=(
        "Lugar"), on_delete=models.CASCADE)
    turno = models.ForeignKey(EntrenamientoTurno, on_delete=models.CASCADE, default="")
    dias = models.ForeignKey(DiasEntrenamiento,verbose_name=("Dias"), on_delete=models.CASCADE)
   

    def __str__(self):
        return f"{self.entrenador}"
    
    def get_duracion(self):
        duracion = self.hasta - self.desde
    
    
