from django.core.exceptions import ValidationError

def validate_field_size(fieldfile_obj):
        try:
            filesize = fieldfile_obj.file.size
        except (OSError, ValueError):
            # archivo ya guardado que no esta en el disco (p. ej. la foto por defecto): no hay nada que medir
            return
        filesize_mb = round((filesize/1024/1024),2)
        megabyte_limit = 2
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("tamaño máximo es de:  %s MB pero estás subiendo un archivo con %s MB" % ( str(megabyte_limit),  str(filesize_mb)))