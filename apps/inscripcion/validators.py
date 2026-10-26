
from django.core.exceptions import ValidationError
import re

def validate_file_size(value):
    filesize = value.size

    if filesize > 2*1028*1028:
        raise ValidationError(
            "El tamaño máximo es de 2Mb")
    else:
        return value

def validar_cuil(cuil):
    """
    Valida un número de CUIL argentino.

    Args:
        cuil (str): El número de CUIL a validar (formato: XX-XXXXXXXX-X).

    Returns:
        bool: True si el CUIL es válido, False en caso contrario.
    """
    # Eliminar guiones y espacios
    cuil = cuil.replace("-", "").replace(" ", "")

    # Verificar la longitud y el formato
    if not re.match(r"^\d{11}$", cuil):
        return False

    # Separar componentes del CUIL
    tipo = int(cuil[0:2])
    numero = int(cuil[2:10])
    digito_verificador = int(cuil[10])

    # Validar el tipo de CUIL
    if tipo not in (20, 23, 24, 27, 30, 33, 34):
        return False

    # Calcular el dígito verificador esperado
    coeficientes = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    suma = 0
    for i in range(10):
        suma += int(cuil[i]) * coeficientes[i]
    resto = suma % 11
    digito_calculado = 11 - resto

    if digito_calculado == 11:
        digito_calculado = 0
    elif digito_calculado == 10:
        return False  # CUIL inválido

    # Comparar el dígito calculado con el proporcionado
    return digito_calculado == digito_verificador