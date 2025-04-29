#!/bin/bash

# CONFIGURACIÓN
DB_NAME="my_database"
BACKUP_FILE="/backups/odoo/my_database_full_20250421_100000.tar.gz"  # reemplaza con tu archivo .tar.gz
FILESTORE_DIR="/opt/odoo/.local/share/Odoo/filestore"
TEMP_DIR="/tmp/odoo_restore"

# Crear carpeta temporal
mkdir -p "$TEMP_DIR"

echo "📦 Desempaquetando backup..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Extraer nombres
SQL_FILE=$(find "$TEMP_DIR" -name "*.sql")
FILESTORE_TAR=$(find "$TEMP_DIR" -name "*filestore*.tar.gz")

echo "🧠 Restaurando base de datos..."
# Crear DB si no existe (requiere privilegios)
createdb -U odoo "$DB_NAME"
psql -U odoo "$DB_NAME" < "$SQL_FILE"

echo "📁 Restaurando filestore..."
tar -xzf "$FILESTORE_TAR" -C "$FILESTORE_DIR"

echo "✅ Restauración completa para base '$DB_NAME' y su filestore."