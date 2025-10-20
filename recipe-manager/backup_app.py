import os
import sys
import json
import subprocess
import datetime
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

    # Extract connection details from the URL
    # Format: mysql+pymysql://user:password@host/dbname
    user = db_url.split('//')[1].split(':')[0]
    password = db_url.split(':')[2].split('@')[0]
    host = db_url.split('@')[1].split('/')[0]
    dbname = db_url.split('/')[-1]

    command = [
        "mysqldump",
        f"--user={user}",
        f"--password={password}",
        f"--host={host}",
        "--ssl=false",
        "--no-tablespaces",
        dbname
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

def main():
    """Main function to run the backup process."""
    # Define a timestamped backup directory
    backup_dir = f"/code/backups/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Created backup directory: {backup_dir}")

    # Set up the database session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Export recipes to JSON
        json_path = os.path.join(backup_dir, "recipes_export.json")
        export_recipes_to_json(session, json_path)

        # 2. Backup the database
        db_path = os.path.join(backup_dir, "database_backup.sql")
        backup_database(db_path)

        # 3. Backup images
        images_source_dir = "/code/app/static/uploads"
        images_path = os.path.join(backup_dir, "image_backup.tar.gz")
        backup_images(images_source_dir, images_path)

        print("\nBackup process completed successfully!")
        print(f"All backup files are located in: {backup_dir}")

    except Exception as e:
        print(f"\nAn error occurred during the backup process: {e}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()