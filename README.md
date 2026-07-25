# mermax
Sistema de Control y Trazabilidad de Mermas en Ensamble de Televisores

Cómo correr el proyecto, paso a paso

1. Preparar la base de datos
# En phpMyAdmin o consola MySQL, confirmar que mermax_db ya existe con las 35 tablas
# (ya lo hiciste, este paso ya está listo)

2. Backend (api)
# Entrar a la carpeta del backend
cd api

# Crear entorno virtual (si no existe)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear la tabla usuario_token (única tabla que Django administra)
python manage.py makemigrations usuarios
python manage.py migrate usuarios

# Levantar el servidor backend (puerto por defecto 8000)
python manage.py runserver

3. Frontend (client)

# En otra terminal, entrar a la carpeta del cliente
cd backend/client

# Activar el mismo entorno virtual (o uno propio si lo separaron)
venv\Scripts\activate

# Instalar dependencias si tiene su propio requirements.txt
pip install -r requirements.txt

# Levantar el servidor cliente en OTRO puerto (para no chocar con el backend)
python manage.py runserver 8001


