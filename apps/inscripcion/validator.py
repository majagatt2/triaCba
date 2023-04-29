from django.core.exceptions import ValidationError


def validate_file_size(value):
    filesize = value.size

    if filesize > 2*1028*1028:
        raise ValidationError(
            "El tamaño máximo es de 2Mb")
    else:
        return value
