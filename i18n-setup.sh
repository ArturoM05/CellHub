#!/bin/bash
# i18n-setup.sh - Configurar gettext para i18n (EN/ES)
# 
# Uso: bash i18n-setup.sh
# Genera estructura de locale y archivos .po para inglés y español

set -e

echo "=== Configurar i18n (gettext) para CellHub ==="

# Crear directorio locale
mkdir -p locale

# Marcar que se generarán mensajes en inglés y español
echo "Generando archivos de mensajes..."

# Generar mensajes base
python manage.py makemessages -l en -i "venv" -i "node_modules" --no-location
python manage.py makemessages -l es -i "venv" -i "node_modules" --no-location

# Compilar mensajes (crea .mo)
python manage.py compilemessages

echo ""
echo "✓ Archivos de i18n generados en locale/"
echo ""
echo "Próximos pasos:"
echo "1. Editar locale/en/LC_MESSAGES/django.po (traducciones EN)"
echo "2. Editar locale/es/LC_MESSAGES/django.po (traducciones ES)"
echo "3. Ejecutar: python manage.py compilemessages"
echo "4. Reiniciar servidor: docker compose restart django_web"
echo ""
echo "Para añadir nuevas cadenas de traducción:"
echo "  - Marcar en Python: from django.utils.translation import gettext as _()"
echo "  - Marcar en templates: {% load i18n %} ... {% trans 'Cadena' %}"
echo "  - Luego: python manage.py makemessages -a"
echo ""
