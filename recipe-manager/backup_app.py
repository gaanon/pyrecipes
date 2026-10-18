import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import joinedload, sessionmaker

from app.database import engine
from app.models import MealPlan, Recipe, RecipeTag

BACKUP_BASE_DIR = Path(os.getenv("BACKUP_DIR", "/code/backups"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/code/uploads"))  # same setting as app/crud.py


class BackupError(Exception):
    pass


def export_recipes_to_json(session, file_path):
    """Exports all recipes and the meal plan to a JSON file (restorable with import_recipes.py)."""
    print("Exporting recipes to JSON...")
    recipes = session.scalars(
        select(Recipe).options(
            joinedload(Recipe.ingredients),
            joinedload(Recipe.instructions),
            joinedload(Recipe.notes),
            joinedload(Recipe.recipe_tags).joinedload(RecipeTag.tag),
        ).order_by(Recipe.id)
    ).unique().all()

    output_data = {"recipes": [], "meal_plans": []}
    for recipe in recipes:
        output_data["recipes"].append({
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
                } for ing in recipe.ingredients
            ],
            "instructions": [
                {"id": inst.id, "step_number": inst.step_number, "description": inst.description}
                for inst in recipe.instructions
            ],
            "notes": [{"id": note.id, "name": note.name, "text": note.text} for note in recipe.notes],
        })
    for meal in session.scalars(select(MealPlan).order_by(MealPlan.plan_date, MealPlan.id)):
        output_data["meal_plans"].append({
            "id": meal.id,
            "plan_date": meal.plan_date.isoformat(),
            "recipe_id": meal.recipe_id,
            "custom_meal_name": meal.custom_meal_name,
        })

    with open(file_path, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Exported {len(output_data['recipes'])} recipes and {len(output_data['meal_plans'])} planned meals to {file_path}")

def _tls_args() -> list[str]:
    """TLS options for whichever mysqldump is installed.

    MySQL 8's default login (caching_sha2_password) needs an encrypted connection (or an RSA
    key exchange), so encrypt; the server's certificate is self-signed, so don't verify it.
    The connection never leaves the private container network.
    """
    version = subprocess.run(["mysqldump", "--version"], capture_output=True, text=True).stdout
    if "MariaDB" in version:  # Debian's default-mysql-client, used in the image
        return ["--ssl", "--skip-ssl-verify-server-cert"]
    return ["--ssl-mode=REQUIRED"]


def _option_value(value: str) -> str:
    # Quoted for the my.cnf format, so passwords with spaces, #, quotes etc. survive
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def backup_database(file_path, db_url=None):
    """Dumps the database to a SQL file. Raises BackupError (leaving no file behind) on failure."""
    print("Backing up the database...")
    db_url = db_url or os.getenv("DATABASE_URL")
    if not db_url:
        raise BackupError("DATABASE_URL environment variable not set")
    url = make_url(db_url)
    file_path = Path(file_path)
    partial = file_path.with_name(file_path.name + ".partial")

    # Credentials go in a private options file: on the command line any process could read them
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as options:
        options.write("[client]\n")
        options.write(f"user={url.username}\n")
        options.write(f"password={_option_value(url.password or '')}\n")
        options.write(f"host={url.host}\n")
        options.write(f"port={url.port or 3306}\n")
    try:
        command = [
            f"--defaults-extra-file={options.name}",  # must be the first option
            "--single-transaction",  # consistent snapshot without locking the tables
            "--no-tablespaces",
            *_tls_args(),
            url.database,
        ]
        with open(partial, "w") as out:
            result = subprocess.run(["mysqldump", *command], stdout=out, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise BackupError(f"mysqldump failed (exit {result.returncode}): {result.stderr.strip()}")
        if "CREATE TABLE" not in partial.read_text():
            raise BackupError("mysqldump produced no tables")
        partial.replace(file_path)
    finally:
        os.unlink(options.name)
        partial.unlink(missing_ok=True)
    print(f"Successfully backed up database to {file_path}")

def backup_images(source_dir, file_path):
    """Creates a tar archive of the photos folder."""
    print("Backing up images...")
    if not os.path.isdir(source_dir):
        print(f"Warning: Image source directory '{source_dir}' not found. Skipping image backup.")
        return
    
    subprocess.run(["tar", "-czf", str(file_path), "-C", str(source_dir), "."], check=True)
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

    # Use `rclone sync` to efficiently update the remote.
    # This command mirrors the source directory to the destination, creating the timestamped folder on the remote.
    command = ["rclone", "sync", source_path, full_remote_path, "--create-empty-src-dirs"]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully synced backup to {full_remote_path}")
    except subprocess.CalledProcessError as e:
        raise BackupError(f"Error syncing to Google Drive: {e.stderr}")


def main(days_to_keep, gdrive_remote, backup_base_dir=BACKUP_BASE_DIR, upload_dir=UPLOAD_DIR, session_factory=None):
    """Runs the backup and rotation. Returns the new backup folder; exits non-zero on failure."""
    backup_base_dir = Path(backup_base_dir)
    backup_dir = backup_base_dir / datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created backup directory: {backup_dir}")

    session = (session_factory or sessionmaker(bind=engine))()
    try:
        export_recipes_to_json(session, backup_dir / "recipes_export.json")
        backup_database(backup_dir / "database_backup.sql")
        backup_images(Path(upload_dir).resolve(), backup_dir / "image_backup.tar.gz")

        print("\nBackup process completed successfully!")
        print(f"All backup files are located in: {backup_dir}")

        if gdrive_remote:
            upload_to_gdrive(str(backup_dir), gdrive_remote)

        if days_to_keep:
            rotate_backups(str(backup_base_dir), days_to_keep)
            if gdrive_remote:
                rotate_gdrive_backups(gdrive_remote, days_to_keep)
    except Exception as e:
        print(f"\nBackup FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()
    return backup_dir

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