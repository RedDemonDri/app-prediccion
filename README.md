# Dashboard Django - MVP (Proyecto)

Resumen
-------
Pequeño dashboard Django (app `dashboard`) preparado como MVP: modelos `MetricCategory`, `Metric`, `MetricValue`, `LogEntry`; vistas `home`, `tabla`; API `/api/chart-data/`; plantillas y assets por CDN y carpeta `dashboard/static`.

Requisitos
----------
- Python 3.11+ instalado
- Entorno virtual (`venv`) activado en la raíz del proyecto
- Django 5.2.5 (recomendado)

Instrucciones (PowerShell)
--------------------------
Abrir PowerShell en la raíz del proyecto (`A - copia`) y activar el venv:

```powershell
.\venv\Scripts\Activate.ps1
```

Hacer backup de la base de datos (recomendado antes de migraciones):

```powershell
copy db.sqlite3 db.sqlite3.bak
```

Aplicar migraciones y crear superusuario (sigue los prompts):

```powershell
python .\dashboard_project\manage.py makemigrations
python .\dashboard_project\manage.py migrate
python .\dashboard_project\manage.py createsuperuser
```

Poblar datos de ejemplo (si quieres usar el script incluido):

```powershell
Get-Content .\dashboard_project\scripts\seed_metrics.py | python .\dashboard_project\manage.py shell
```

Iniciar servidor de desarrollo:

```powershell
python .\dashboard_project\manage.py runserver
```

URLs relevantes
---------------
- Home: `http://127.0.0.1:8000/`
- Tabla: `http://127.0.0.1:8000/tabla/`
- Admin: `http://127.0.0.1:8000/admin/`
- API chart data: `http://127.0.0.1:8000/api/chart-data/`

Archivos importantes
-------------------
- `dashboard/models.py` — modelos principales
- `dashboard/admin.py` — registro en admin
- `dashboard/views.py` — `home`, `tabla`, `chart_data`
- `dashboard/urls.py` — rutas de la app
- `templates/` y `dashboard/templates/` — plantillas
- `dashboard/static/` — assets estáticos (CSS/JS/imagenes)
- `dashboard/migrations/` — migraciones (se aplicaron correcciones)
- `dashboard_project/settings.py` — configuración (templates/static integrados)

Static files en desarrollo
--------------------------
- `STATICFILES_DIRS` incluye `dashboard/static/` para que Django sirva esos assets en dev.
- `STATIC_URL` está configurado como `/static/` y `STATIC_ROOT` es `staticfiles/` (útil para `collectstatic`).

Problemas comunes y soluciones
------------------------------
- TemplateDoesNotExist: verificar `TEMPLATES['DIRS']` en `dashboard_project/settings.py` y que la plantilla exista en `templates/` o `dashboard/templates/`.
- Field 'id' expected a number but got 'default': ocurre si una migración asignó `default='default'` a una FK. Ya se aplicó una corrección en `dashboard/migrations/0002...` y `0003_fix_default_category.py` para reemplazar cadenas 'default' por una `MetricCategory` real.
- DB locked: cerrar procesos/terminales que usen la DB o reiniciar el servidor.

Verificaciones ejecutadas
-------------------------
- `manage.py check` — sin errores
- Migraciones aplicadas y servidor de desarrollo arrancado localmente (ver historial de comandos).

Siguientes pasos recomendados
----------------------------
- Hacer commit de estos cambios y migraciones corregidas:
```powershell
git add .
git commit -m "MVP: modelos, vistas, templates, corrección migraciones y README"
```
- Añadir `requirements.txt` si lo deseas: `pip freeze > requirements.txt`

Contacto / notas
----------------
Si quieres que haga el commit aquí, dime `commit` y lo hago. También puedo:
- Renombrar la categoría por defecto (`default`) a `No asignada`.
- Añadir pruebas unitarias básicas para `home` y `chart_data`.
- Preparar un `Dockerfile` simple o `requirements.txt`.

---
README generado automáticamente por el asistente. Si quieres cambios en el texto o añadir secciones, dime qué prefieres.
