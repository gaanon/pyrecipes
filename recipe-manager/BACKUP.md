# Recipe Manager Backup & Restore Guide

This guide provides the definitive instructions for backing up and restoring the Recipe Manager application data.

## 1. Automated Backup

A single, self-contained script, `backup_app.py`, handles the entire backup process. It runs entirely within the application's container, making it robust and reliable across different environments.

The script will create a timestamped directory inside the `recipe-manager/backups` folder and save three files:
- `recipes_export.json`: A JSON export of all your recipes.
- `database_backup.sql`: A complete SQL dump of your database.
- `image_backup.tar.gz`: A compressed archive of all your uploaded images.

### To run the backup:
Execute the following command from the `recipe-manager` directory:
```bash
docker-compose exec app python backup_app.py
```

## 2. Restore Process

### Restore the Database
To restore the database from a SQL dump, run the following command from the `recipe-manager` directory. Replace the path with the correct path to your backup file.

**Example:**
```bash
docker-compose exec -T db mysql -u user -ppassword recipe_db < backups/2025-10-20_12-08-54/database_backup.sql
```

### Restore the Images
To restore your uploaded images, extract the `image_backup.tar.gz` archive into the correct directory.

**Example:**
```bash
tar -xzvf backups/2025-10-20_12-08-54/image_backup.tar.gz -C app/static/uploads
```

### Restore Recipes from JSON
To restore recipes from a JSON file (which will update existing recipes and create new ones), use the `import_recipes.py` script.

**Example:**
```bash
docker-compose exec app python import_recipes.py backups/2025-10-20_12-08-54/recipes_export.json
```

## 3. Schedule Daily Backups

To automate the backup process, you can schedule the `backup_app.py` script to run daily using a cron job.

1.  Open your crontab for editing:
    ```bash
    crontab -e
    ```

2.  Add the following line, making sure to replace `/path/to/your/recipe-manager` with the absolute path to your `recipe-manager` directory:
    ```bash
    0 2 * * * cd /path/to/your/recipe-manager && docker-compose exec app python backup_app.py
    ```
This will run the backup every day at 2:00 AM.