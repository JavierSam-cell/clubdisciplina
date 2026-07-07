from django import forms
from .models import Post, Receta, Frase


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('tipo', 'texto', 'imagen')
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 2, 'placeholder': '¿Qué quieres compartir?'}),
        }


class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ('titulo', 'categoria', 'ingredientes', 'preparacion', 'imagen')
        widgets = {
            'ingredientes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Un ingrediente por línea'}),
            'preparacion': forms.Textarea(attrs={'rows': 5}),
        }


class FraseComunidadForm(forms.ModelForm):
    """Formulario simple para que una usuaria comparta una frase que le gustó."""
    class Meta:
        model = Frase
        fields = ('texto', 'momento')
        widgets = {
            'texto': forms.Textarea(
                attrs={'rows': 2, 'placeholder': 'Ej. "La disciplina siempre vence al talento."'}
            ),
        }
        labels = {
            'momento': '¿En qué momento crees que le sirve más a alguien esta frase?',
        }
