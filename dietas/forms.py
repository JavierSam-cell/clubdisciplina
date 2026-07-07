from django import forms
from django.forms import inlineformset_factory

from .models import Dieta, DietaComida


class DietaForm(forms.ModelForm):
    class Meta:
        model = Dieta
        fields = [
            'nombre', 'categoria', 'objetivo', 'preferencia', 'presupuesto',
            'comidas_por_dia', 'calorias_aproximadas', 'descripcion',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'nombre': 'Nombre de la dieta',
        }


# Permite armar el menú del día (agregar comidas en orden) en la misma
# pantalla, igual que en el admin de Django pero desde el sitio.
DietaComidaFormSet = inlineformset_factory(
    Dieta,
    DietaComida,
    fields=['comida', 'orden'],
    extra=4,
    can_delete=True,
)
