from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class RegistroForm(UserCreationForm):
    """
    Formulario de registro = cuestionario inicial.
    Extiende el formulario de creación de usuario de Django (que ya
    valida username/password) y le agrega todos los campos del perfil.
    """
    nombre_para_mostrar = forms.CharField(
        max_length=50, label="¿Cómo quieres que te llamemos?",
        widget=forms.TextInput(attrs={'placeholder': 'Ej. María'})
    )
    edad = forms.IntegerField(min_value=12, max_value=100, label="Edad")
    estatura_cm = forms.IntegerField(min_value=120, max_value=220, label="Estatura (cm)")
    peso_inicial_kg = forms.DecimalField(
        min_value=30, max_value=300, decimal_places=1, label="Peso actual (kg)"
    )
    cintura_inicial_cm = forms.DecimalField(
        min_value=40, max_value=200, decimal_places=1, label="Cintura (cm)"
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = (
            'username', 'email', 'nombre_para_mostrar',
            'edad', 'estatura_cm', 'peso_inicial_kg', 'cintura_inicial_cm',
            'objetivo', 'lugar_entreno', 'nivel', 'minutos_disponibles',
            'lesiones', 'horario_preferido',
            'preferencia_alimenticia', 'presupuesto_comida',
            'tono_mensajes',
        )
        widgets = {
            'lesiones': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Opcional. Ej. dolor de rodilla.'}),
        }
        labels = {
            'objetivo': '¿Cuál es tu objetivo principal?',
            'lugar_entreno': '¿Dónde vas a entrenar?',
            'nivel': '¿Cuál es tu nivel actual?',
            'minutos_disponibles': '¿Cuántos minutos tienes disponibles por sesión?',
            'horario_preferido': '¿En qué horario prefieres entrenar?',
            'preferencia_alimenticia': '¿Cómo describirías tu forma de comer?',
            'presupuesto_comida': '¿Cuál es tu presupuesto para la comida?',
            'tono_mensajes': '¿Cómo prefieres que te hablemos?',
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.cintura_inicial_cm = self.cleaned_data['cintura_inicial_cm']
        if commit:
            usuario.save()
        return usuario


class PerfilForm(forms.ModelForm):
    """Para editar el perfil ya con la cuenta creada (sección 'Mi cuenta')."""
    class Meta:
        model = Usuario
        fields = (
            'nombre_para_mostrar', 'objetivo', 'lugar_entreno', 'nivel',
            'minutos_disponibles', 'lesiones', 'horario_preferido',
            'preferencia_alimenticia', 'presupuesto_comida', 'tono_mensajes',
        )
        widgets = {
            'lesiones': forms.Textarea(attrs={'rows': 2}),
        }
