#!/bin/bash

# Create a timestamped directory for the backup
BACKUP_DIR="backups/$(date +%Y-%m-%d_%H-%M-%S)"
mkdir -p "$BACKUP_DIR"

# 1. Export recipes to JSON
echo "Exporting recipes to JSON..."
docker-compose exec -T app python export_recipes.py
mv backups/recipes_export.json "$BACKUP_DIR/"

# 2. Dump the database
echo "Dumping the database..."
docker-compose exec -T db mysqldump --no-tablespaces -u user -ppassword recipe_db > "$BACKUP_DIR/database_backup.sql"

# 3. Archive the images
echo "Archiving images..."
tar -czvf "$BACKUP_DIR/image_backup.tar.gz" -C app/static/uploads .

echo "Backup complete. Files are in $BACKUP_DIR"