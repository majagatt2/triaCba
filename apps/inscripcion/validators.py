import os
from django.core.exceptions import ValidationError


def validate_file_size(value):
    filesize = value.size

    if filesize > 2*1028*1028:
        raise ValidationError(
            "El tamaño máximo es de 2Mb")
    else:
        return value
    

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.jpg', '.png', '.jpeg',]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Sólo puedes subir '.pdf', '.jpg', '.png', '.jpeg'")
