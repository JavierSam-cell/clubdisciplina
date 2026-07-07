from django import forms
from django.forms import inlineformset_factory

from .models import Rutina, RutinaEjercicio


class RutinaForm(forms.ModelForm):
    class Meta:
        model = Rutina
        fields = [
            'nombre', 'categoria', 'lugar', 'nivel', 'equipo',
            'tipo_cardio', 'minutos_duracion', 'descripcion',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'nombre': 'Nombre de la rutina',
            'minutos_duracion': 'Duración aproximada (minutos)',
        }


# Permite agregar los ejercicios de la rutina (en orden) en la misma pantalla,
# igual que en el admin de Django pero desde el sitio.
RutinaEjercicioFormSet = inlineformset_factory(
    Rutina,
    RutinaEjercicio,
    fields=['ejercicio', 'orden', 'series', 'repeticiones', 'descanso_segundos'],
    extra=3,
    can_delete=True,
)
