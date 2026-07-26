Ya está reportes (RF-11 a RF-14). Para probarlo:

1. Actualizar — en este orden, si no truena:

git pull origin main
pip install reportlab

Importar mermax.sql en phpMyAdmin (raíz del servidor, no entren a la base), y luego:

cd api
python manage.py migrate
python manage.py seed_demo --mermas 200
python manage.py runserver

2. Sacar el token — en otra terminal, con el venv activado:

```powershell
$d = Invoke-RestMethod -Uri http://127.0.0.1:8000/api/usuarios/login/ -Method Post -ContentType "application/json" -Body '{"username":"diego","password":"123"}'
```

3. El PDF (RF-14):

powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/reportes/mermas/pdf/?linea=3" -Headers $h -OutFile reporte.pdf
powershell
Invoke-Item reporte.pdf

4. El dashboard (RF-12):

powershell
(Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/reportes/dashboard/" -Headers $h).por_linea | Format-Table linea_nombre, porcentaje_scrap, umbral, semaforo

Filtros que aceptan el reporte y el PDF, solos o combinados:
?linea=3&turno=NOC&tipo_merma=DEF_FAB&causa_raiz=CONTAM&desde=2026-06-01&hasta=2026-07-25

Sin /pdf/ los devuelve en JSON.

Otros endpoints:

GET /api/reportes/trazabilidad/lote/3/ — ciclo completo del lote (RF-11)
POST /api/reportes/alertas/evaluar/ — genera alertas por umbral rebasado (RF-13)
GET /api/reportes/alertas/?estado=ACTIVA
POST /api/reportes/alertas/1/atender/ con {"observaciones":"..."} — sólo rol CALID o ADMIN

Dos cosas: no abran los endpoints en el navegador, dan 401 porque la API sólo acepta el header Authorization: Token. Y cada vez que reimporten el SQL hay que volver a hacer login: los tokens no sobreviven.