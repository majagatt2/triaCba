from django import forms

from .envios import EMAIL_ASOCIACION, GRUPOS
from .models import Newsletter

TAMANO_MAX_ADJUNTOS_MB = 8   # Gmail admite hasta 25 MB por mail; se deja margen


class VariosArchivos(forms.ClearableFileInput):
    allow_multiple_selected = True


class NewsletterCreationForm(forms.ModelForm):
    adjuntos = forms.FileField(
        required=False, label='Adjuntos (imágenes o PDF)',
        widget=VariosArchivos(attrs={'multiple': True, 'accept': 'image/*,.pdf', 'class': 'form-control'}),
        help_text=f'Opcional. Van adjuntos a cada mail (máximo {TAMANO_MAX_ADJUNTOS_MB} MB en total). '
                  'Para que una imagen se vea DENTRO del texto, usá el botón de imagen del editor.')

    class Meta:
        model = Newsletter
        fields = ['subject', 'body', 'email', 'bcc', 'status']
        labels = {
            'subject': 'Asunto',
            'body': 'Mensaje',
            'email': 'Para',
            'bcc': 'Destinatarios',
            'status': 'Acción',
        }
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            # el cuerpo usa el editor del modelo (RichTextUploadingField): permite imagenes, links, formato
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, eventos=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = EMAIL_ASOCIACION
        self.fields['email'].help_text = 'Además del grupo elegido. Normalmente la cuenta de la Asociación.'
        opciones = list(GRUPOS) + [(str(e.pk), f'Inscriptos: {e}') for e in eventos]
        self.fields['bcc'].widget = forms.Select(choices=opciones, attrs={'class': 'form-select'})
        self.fields['status'].choices = [('Borrador', 'Guardar como borrador'), ('Publicar', 'Enviar al grupo')]

    def archivos(self):
        return self.files.getlist('adjuntos') if self.files else []

    def clean(self):
        datos = super().clean()
        total = sum(a.size for a in self.archivos())
        if total > TAMANO_MAX_ADJUNTOS_MB * 1024 * 1024:
            raise forms.ValidationError(f'Los adjuntos suman {total / 1024 / 1024:.1f} MB; el máximo es '
                                        f'{TAMANO_MAX_ADJUNTOS_MB} MB.')
        return datos
