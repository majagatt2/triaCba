from django import forms
from .models import Newsletter



class NewsletterCreationForm(forms.ModelForm):

    class Meta:
        model = Newsletter
        fields = ['subject', 'body', 'email', 'bcc', 'status']

        labels = {

            #'name': 'Name',
            'subject': 'Título',
            'body': 'Mensaje:',
            'email': 'Para:',
            'bcc': "CCO:",
            'status': 'Status',

        }

        widgets = {

            #'name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control'}),
            #'email': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),





        }
