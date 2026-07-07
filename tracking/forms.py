from django import forms
from .models import RegistroDiario, FotoProgreso


class RegistroDiarioForm(forms.ModelForm):
    class Meta:
        model = RegistroDiario
        fields = (
            'entreno', 'minutos_entrenados', 'tomo_agua_meta',
            'horas_sueno', 'peso_kg', 'cintura_cm', 'momento_dificil',
        )
        widgets = {
            'momento_dificil': forms.TextInput(
                attrs={'placeholder': '¿Qué fue lo más difícil hoy? (opcional)'}
            ),
        }
        labels = {
            'entreno': '¿Entrenaste hoy?',
            'minutos_entrenados': 'Minutos entrenados',
            'tomo_agua_meta': '¿Cumpliste tu meta de agua?',
            'horas_sueno': 'Horas de sueño anoche',
            'peso_kg': 'Peso de hoy (kg) — opcional',
            'cintura_cm': 'Cintura (cm) — opcional',
        }


class FotoProgresoForm(forms.ModelForm):
    class Meta:
        model = FotoProgreso
        fields = ('imagen', 'fecha', 'nota')
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'nota': forms.TextInput(attrs={'placeholder': 'Ej. "Semana 4" (opcional)'}),
        }
        labels = {
            'imagen': 'Foto',
            'fecha': 'Fecha de la foto',
            'nota': 'Nota (opcional)',
        }
