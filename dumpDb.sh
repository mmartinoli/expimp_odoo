#!/bin/bash

# CONFIGURACIÓN
DB_NAME="my_database"                 # nombre de la base de datos
BACKUP_DIR="/backups/odoo"           # carpeta donde guardar los backups
FILESTORE_DIR="/opt/odoo/.local/share/Odoo/filestore"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DUMP_FILE="$BACKUP_DIR/${DB_NAME}_$TIMESTAMP.sql"
FILESTORE_BACKUP="$BACKUP_DIR/${DB_NAME}_filestore_$TIMESTAMP.tar.gz"
FULL_BACKUP="$BACKUP_DIR/${DB_NAME}_full_$TIMESTAMP.tar.gz"

# Crear carpeta de backup si no existe
mkdir -p "$BACKUP_DIR"

echo "📦 Realizando backup de base de datos..."
pg_dump -U odoo "$DB_NAME" > "$DUMP_FILE"

echo "📁 Comprimiendo filestore..."
tar -czf "$FILESTORE_BACKUP" -C "$FILESTORE_DIR" "$DB_NAME"

echo "🗃️ Empaquetando backup completo..."
tar -czf "$FULL_BACKUP" -C "$BACKUP_DIR" "$(basename "$DUMP_FILE")" "$(basename "$FILESTORE_BACKUP")"

echo "✅ Backup completo generado en: $FULL_BACKUP"

# (Opcional) limpiar archivos temporales si solo querés quedarte con el .tar.gz final:
# rm "$DUMP_FILE" "$FILESTORE_BACKUP"