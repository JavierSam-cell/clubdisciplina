import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0001_initial'),
    ]

    operations = [
        # --- El reto "de un solo título" desaparece; ahora vive en ItemRetoSemanal ---
        migrations.RemoveField(model_name='retosemanal', name='titulo'),
        migrations.RemoveField(model_name='retosemanal', name='descripcion'),
        migrations.AddField(
            model_name='retosemanal',
            name='generado_automaticamente',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterModelOptions(
            name='retosemanal',
            options={'ordering': ['-fecha_inicio']},
        ),
        migrations.AlterField(
            model_name='retosemanal',
            name='fecha_inicio',
            field=models.DateField(unique=True),
        ),

        # --- Ya no hay una sola "participación por reto": ahora es por ítem ---
        migrations.DeleteModel(name='ParticipacionReto'),

        migrations.CreateModel(
            name='OpcionRetoBiblioteca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoria', models.CharField(
                    choices=[
                        ('agua', '💧 Agua'),
                        ('entrenamiento', '🏋️ Entrenamiento'),
                        ('alimentacion', '🥗 Alimentación'),
                        ('mental', '🧘 Mental'),
                        ('foto_progreso', '📷 Foto de progreso'),
                    ], max_length=20)),
                ('texto', models.CharField(help_text="Ej. 'Entrena 4 días' o 'Toma 2 litros de agua'.", max_length=150)),
                ('puntos', models.PositiveSmallIntegerField(default=20)),
                ('activo', models.BooleanField(
                    default=True,
                    help_text='Desactívala para dejar de usarla en semanas nuevas sin borrar el historial ya generado.'
                )),
            ],
            options={
                'ordering': ['categoria', 'texto'],
            },
        ),
        migrations.CreateModel(
            name='ItemRetoSemanal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoria', models.CharField(
                    choices=[
                        ('agua', '💧 Agua'),
                        ('entrenamiento', '🏋️ Entrenamiento'),
                        ('alimentacion', '🥗 Alimentación'),
                        ('mental', '🧘 Mental'),
                        ('foto_progreso', '📷 Foto de progreso'),
                    ], max_length=20)),
                ('texto', models.CharField(max_length=150)),
                ('puntos', models.PositiveSmallIntegerField(default=20)),
                ('opcion', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='usos', to='community.opcionretobiblioteca'
                )),
                ('reto_semanal', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='items', to='community.retosemanal'
                )),
            ],
            options={
                'ordering': ['categoria'],
            },
        ),
        migrations.CreateModel(
            name='ParticipacionItemReto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completado', models.BooleanField(default=False)),
                ('fecha_completado', models.DateTimeField(blank=True, null=True)),
                ('item', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='participaciones', to='community.itemretosemanal'
                )),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('item', 'usuario')},
            },
        ),
        migrations.CreateModel(
            name='PuntosEvento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntos', models.SmallIntegerField()),
                ('motivo', models.CharField(
                    choices=[('reto', 'Reto semanal completado'), ('racha', 'Bono de racha')], max_length=10
                )),
                ('detalle', models.CharField(blank=True, max_length=200)),
                ('creado', models.DateTimeField(default=django.utils.timezone.now)),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, related_name='puntos_eventos', to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'ordering': ['-creado'],
            },
        ),
    ]
