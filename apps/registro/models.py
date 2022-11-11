from django.db import models
from ckeditor.fields import RichTextField


class Bienvenida(models.Model):
    mensaje = RichTextField()
    
    def __str__(self):
        return f"{self.mensaje}"
    
