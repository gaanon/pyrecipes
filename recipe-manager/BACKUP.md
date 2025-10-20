# Recipe Manager Backup Guide

This guide provides instructions for backing up the Recipe Manager application data.

## 1. Database Backup

To create a full backup of the application database, you can use the `mysqldump` utility. This command should be run from within the `recipe-manager` directory.

```bash
docker-compose exec -T db mysqldump -u user -ppassword recipe_db > database_backup.sql
```

This command will create a file named `database_backup.sql` in the `recipe-manager` directory, containing a complete snapshot of your database.

## 2. Image Backup

The recipe images are stored in the `recipe-manager/app/static/uploads` directory. To back them up, you can create a compressed archive of this folder.

```bash
tar -czvf image_backup.tar.gz -C recipe-manager/app/static/uploads .
```

This command will create a file named `image_backup.tar.gz` in the current directory, containing all the uploaded images.

## 3. Automated Backup Script

A comprehensive backup script, `backup.sh`, is provided to automate the entire backup process. This script will create a timestamped directory in the `backups` folder and save the JSON export, database dump, and image archive.

To run the script, execute the following command from the `recipe-manager` directory:

```bash
./backup.sh
```

## 4. Schedule Daily Backups

To ensure your data is backed up regularly, you can schedule the `backup.sh` script to run automatically every day using a cron job.

1.  Open your crontab file for editing:

    ```bash
    crontab -e
    ```

2.  Add the following line to the file, making sure to replace `/path/to/your/recipe-manager` with the absolute path to your `recipe-manager` directory:

    ```bash
    0 2 * * * /path/to/your/recipe-manager/backup.sh
    ```

This will schedule the backup script to run every day at 2:00 AM.

# Restore Process

This guide provides instructions for restoring the Recipe Manager application data from a backup.

## 1. Restore the Database

To restore the database from a SQL dump, you can use the `mysql` client. This command should be run from within the `recipe-manager` directory, and you should replace `database_backup.sql` with the path to your backup file.

```bash
docker-compose exec -T db mysql -u user -ppassword recipe_db < database_backup.sql
```

## 2. Restore the Images

To restore the images, you'll need to extract the `image_backup.tar.gz` archive into the `recipe-manager/app/static/uploads` directory.

```bash
tar -xzvf image_backup.tar.gz -C recipe-manager/app/static/uploads
```

## 3. Import Recipes from JSON

If you need to restore the recipes from a JSON export, you can use the `import_recipes.py` script. This script will update existing recipes and create new ones as needed.

Run the following command from the `recipe-manager` directory, replacing `path/to/your/recipes_export.json` with the actual path to your JSON backup file.

**Example:**

```bash
docker-compose exec app python import_recipes.py backups/2025-10-20_10-52-22/recipes_export.json
```