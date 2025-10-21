import os
import sys
import json
import subprocess
import datetime
import argparse
import shutil
from sqlalchemy.orm import sessionmaker, joinedload
from app.database import engine
from app.models import Recipe, RecipeTag

def export_recipes_to_json(session, file_path):
    """Exports all recipes to a JSON file."""
    print("Exporting recipes to JSON...")
    recipes = session.query(Recipe).options(
        joinedload(Recipe.ingredients),
        joinedload(Recipe.instructions),
        joinedload(Recipe.notes),
        joinedload(Recipe.recipe_tags).joinedload(RecipeTag.tag)
    ).all()

    output_data = {"recipes": []}
    for recipe in recipes:
        recipe_data = {
            "id": recipe.id,
            "name": recipe.name,
            "servings": recipe.servings,
            "photo_path": recipe.photo_path,
            "tags": [rt.tag.name for rt in recipe.recipe_tags],
            "ingredients": [
                {
                    "id": ing.id, "name": ing.name, "amount": ing.amount,
                    "group_name": ing.group_name, "is_optional": ing.is_optional,
                    "order_index": ing.order_index
                } for ing in sorted(recipe.ingredients, key=lambda x: x.order_index)
            ],
            "instructions": [
                {
                    "id": inst.id, "step_number": inst.step_number,
                    "description": inst.description
                } for inst in sorted(recipe.instructions, key=lambda x: x.step_number)
            ],
            "notes": [
                {"id": note.id, "name": note.name, "text": note.text}
                for note in recipe.notes
            ]
        }
        output_data["recipes"].append(recipe_data)

    with open(file_path, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Successfully exported recipes to {file_path}")

def backup_database(file_path):
    """Dumps the database to a SQL file."""
    print("Backing up the database...")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL environment variable not set.")
        sys.exit(1)

    user = db_url.split('//')[1].split(':')[0]
    password = db_url.split(':')[2].split('@')[0]
    host = db_url.split('@')[1].split('/')[0]
    dbname = db_url.split('/')[-1]

    command = [
        "mysqldump", f"--user={user}", f"--password={password}",
        f"--host={host}", "--ssl=false", "--no-tablespaces", dbname
    ]
    with open(file_path, 'w') as f:
        subprocess.run(command, stdout=f, check=True)
    print(f"Successfully backed up database to {file_path}")

def backup_images(source_dir, file_path):
    """Creates a tar archive of the images directory."""
    print("Backing up images...")
    if not os.path.isdir(source_dir):
        print(f"Warning: Image source directory '{source_dir}' not found. Skipping image backup.")
        return
    
    command = ["tar", "-czvf", file_path, "-C", source_dir, "."]
    subprocess.run(command, check=True)
    print(f"Successfully backed up images to {file_path}")

def rotate_backups(backup_base_dir, days_to_keep):
    """Removes backup directories older than a specified number of days."""
    if days_to_keep <= 0:
        return

    print(f"\nRotating backups. Keeping the last {days_to_keep} days...")
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=days_to_keep)

    for dirname in os.listdir(backup_base_dir):
        dir_path = os.path.join(backup_base_dir, dirname)
        if not os.path.isdir(dir_path):
            continue

        try:
            backup_time = datetime.datetime.strptime(dirname, '%Y-%m-%d_%H-%M-%S')
            if backup_time < cutoff:
                print(f"Deleting old backup directory: {dir_path}")
                shutil.rmtree(dir_path)
        except (ValueError, TypeError):
            print(f"Skipping non-backup directory: {dir_path}")
            continue
    print("Backup rotation complete.")


def rotate_gdrive_backups(remote_path, days_to_keep):
    """Removes backup directories from Google Drive older than a specified number of days."""
    if days_to_keep <= 0:
        return

    print(f"\nRotating Google Drive backups. Keeping the last {days_to_keep} days...")
    if not remote_path:
        print("Warning: Google Drive remote path not configured. Skipping rotation.")
        return

    min_age = f"{days_to_keep}d"
    # Delete files older than min_age, then remove the resulting empty directories.
    delete_command = ["rclone", "delete", remote_path, "--min-age", min_age]
    rmdirs_command = ["rclone", "rmdirs", remote_path]

    try:
        print(f"Deleting files older than {days_to_keep} days from {remote_path}...")
        subprocess.run(delete_command, check=True, capture_output=True, text=True)
        print("Deleting empty backup directories from Google Drive...")
        subprocess.run(rmdirs_command, check=True, capture_output=True, text=True)
        print("Google Drive backup rotation complete.")
    except subprocess.CalledProcessError as e:
        # Don't exit on rotation failure, just warn the user.
        print(f"Warning: Error during Google Drive backup rotation: {e.stderr}")


def upload_to_gdrive(source_path, remote_path):
    """Uploads a directory to Google Drive using rclone, preserving the source directory structure."""
    print("\nUploading backup to Google Drive...")
    if not remote_path:
        print("Warning: Google Drive remote path not configured. Skipping upload.")
        return

    # Append the backup directory name to the remote path to keep the timestamped structure
    backup_dirname = os.path.basename(source_path)
    # rclone uses forward slashes for paths
    full_remote_path = remote_path.rstrip('/') + '/' + backup_dirname

    command = ["rclone", "copy", source_path, full_remote_path, "--create-empty-src-dirs"]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully uploaded backup to {full_remote_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error uploading to Google Drive: {e.stderr}")
        sys.exit(1)


def main(days_to_keep, gdrive_remote):
    """Main function to run the backup and rotation process."""
    backup_base_dir = "/code/backups"
    backup_dir = os.path.join(backup_base_dir, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Created backup directory: {backup_dir}")

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        json_path = os.path.join(backup_dir, "recipes_export.json")
        export_recipes_to_json(session, json_path)

        db_path = os.path.join(backup_dir, "database_backup.sql")
        backup_database(db_path)

        images_source_dir = "/code/app/static/uploads"
        images_path = os.path.join(backup_dir, "image_backup.tar.gz")
        backup_images(images_source_dir, images_path)

        print("\nBackup process completed successfully!")
        print(f"All backup files are located in: {backup_dir}")

        if gdrive_remote:
            upload_to_gdrive(backup_dir, gdrive_remote)

        if days_to_keep:
            rotate_backups(backup_base_dir, days_to_keep)
            if gdrive_remote:
                rotate_gdrive_backups(gdrive_remote, days_to_keep)

    except Exception as e:
        print(f"\nAn error occurred during the backup process: {e}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a complete backup of the Recipe Manager application and rotates old backups.",
        epilog="This script creates a timestamped backup including a JSON export, a database dump, and an image archive."
    )
    parser.add_argument(
        "--days-to-keep",
        type=int,
        default=0,
        help="The number of days to keep backups. Older backups will be deleted. Set to 0 to keep all backups."
    )
    parser.add_argument(
        "--gdrive-remote",
        type=str,
        default="",
        help="The rclone remote path for Google Drive backup (e.g., gdrive:backups)."
    )
    args = parser.parse_args()
    main(args.days_to_keep, args.gdrive_remote)