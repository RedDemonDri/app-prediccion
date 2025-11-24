#!/usr/bin/env python
"""
Wrapper manage.py en la raíz del repo para delegar a dashboard_project.manage
Permite ejecutar `python manage.py` desde la raíz sin cambiar de directorio.
"""
import os
import sys


if __name__ == "__main__":
    # Añadimos dashboard_project al path para que Django pueda importar settings
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(base_dir, 'dashboard_project'))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')

    try:
        from django.core.management import execute_from_command_line
    except Exception:
        # Intentar importar Django usando ruta relativa a venv si existe
        raise

    execute_from_command_line(sys.argv)
