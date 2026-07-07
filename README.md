# Proyecto Disciplina

Plataforma web (Django) para el club de disciplina y ejercicio.

## Qué incluye esta primera versión

- **Registro con cuestionario inicial** (`/registro/`): crea la cuenta y captura edad, peso,
  estatura, cintura, objetivo, lugar de entreno, nivel, minutos disponibles, lesiones,
  horario y **tono de mensajes** (suave o directo).
- **Dashboard** (`/club/`): saludo personalizado, día del compromiso, racha actual
  ("NO ROMPAS LA CADENA"), frase del día (personalizada según el momento de la usuaria),
  reto semanal activo y medallas recientes.
- **Check-in diario** (`/club/registro-diario/`): entrenó o no, minutos, agua, sueño, peso, cintura.
- **Rutinas** (`/rutinas/`): recomendadas automáticamente según el perfil de la usuaria
  (lugar de entreno, nivel y minutos disponibles), con filtros para explorar todo el catálogo,
  detalle paso a paso de cada rutina (series/repeticiones/descanso), y **biblioteca de técnica**
  (`/rutinas/biblioteca/`) con la explicación de cómo hacer cada ejercicio, filtrable por grupo muscular.
- **Comunidad**:
  - Feed de publicaciones con reacciones rápidas (`/comunidad/`)
  - Recetas compartidas por cualquier usuaria, con categorías y **moderación** (`/comunidad/recetas/`)
  - Frases compartidas por la comunidad, también con moderación (`/comunidad/frases/`)
  - Ranking por **constancia** (racha), no por kilos (`/comunidad/ranking/`)
  - Compañera de compromiso / buddy system (`/comunidad/mi-companera/`)
- **Panel de administración** (`/admin/`) para moderar recetas y frases antes de que se publiquen,
  gestionar usuarias, medallas y retos semanales.

## Cómo correrlo en tu computadora

Necesitas tener **Python 3.11 o superior** instalado.

### 1. Crear el entorno virtual e instalar dependencias

```bash
cd clubdisciplina          # la carpeta donde descomprimiste el proyecto
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate        # en Mac/Linux
venv\Scripts\activate            # en Windows (cmd)

pip install -r requirements.txt
```

### 2. Crear la base de datos

```bash
python manage.py migrate
```

### 3. Cargar contenido inicial (frases del sistema, medallas, un reto de ejemplo)

```bash
python manage.py seed_inicial
```

### 4. Crear tu usuario de administrador

```bash
python manage.py createsuperuser
```

Te va a pedir username, correo y contraseña. Con esa cuenta entras a `/admin/` para moderar
recetas y frases, y para editar el catálogo de medallas y los retos semanales.

### 5. Levantar el servidor

```bash
python manage.py runserver
```

Abre tu navegador en **http://127.0.0.1:8000/**

## Moderación de contenido de la comunidad

Cuando alguien sube una receta o comparte una frase, **no se publica automáticamente**.
Entra a `/admin/` → sección "Community" → "Recetas" o "Frases", revisa el contenido pendiente
(aparece primero en la lista) y usa la acción **"Aprobar elementos seleccionados"**.

## Próximos pasos sugeridos (no incluidos todavía)

- Emparejamiento automático de "compañera de compromiso" según objetivo/horario
  (por ahora se asigna manualmente desde el admin, creando un registro en
  "CompaneraDeCompromiso").
- Cálculo automático de medallas ganadas (por ahora el catálogo existe, pero
  otorgarlas automáticamente al cumplir la condición se puede agregar como
  una tarea programada).
- Subida de fotos de progreso con comparación antes/después.
- Diez dietas filtradas por perfil (económica, vegetariana, mexicana, etc.) — mismo patrón que rutinas.
- Despliegue a producción (hosting, dominio, `DEBUG = False`, variables de entorno,
  base de datos PostgreSQL en vez de SQLite).

## Estructura del proyecto

```
clubdisciplina/
├── accounts/       # Usuario personalizado, registro, login, "mi cuenta"
├── tracking/        # Registro diario, rachas, medallas, dashboard
├── rutinas/          # Biblioteca de ejercicios y rutinas filtradas por perfil
├── community/         # Feed, recetas, frases, ranking, buddy system, retos
├── templates/          # base.html (layout compartido)
└── clubdisciplina/     # configuración del proyecto (settings, urls)
```
