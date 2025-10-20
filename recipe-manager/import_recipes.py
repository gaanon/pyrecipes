import json
import os
import sys
import argparse
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import Base, Recipe, Ingredient, Instruction, Note, Tag, RecipeTag

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def import_recipes(file_path):
    """
    Reads recipes from a JSON file and imports them into the database.
    Updates existing recipes based on ID, or creates new ones.
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    print(f"Importing recipes from {file_path}...")

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        existing_tags = session.query(Tag).all()
        tags_map = {tag.name: tag for tag in existing_tags}

        for recipe_data in data['recipes']:
            recipe_id = recipe_data.get('id')
            
            db_recipe = session.query(Recipe).filter(Recipe.id == recipe_id).first()

            if db_recipe:
                print(f"Updating recipe: {recipe_data['name']}")
                db_recipe.name = recipe_data['name']
                db_recipe.servings = recipe_data.get('servings')
                db_recipe.photo_path = recipe_data.get('photo_path')
                
                db_recipe.ingredients.clear()
                db_recipe.instructions.clear()
                db_recipe.notes.clear()
                db_recipe.recipe_tags.clear()
            else:
                print(f"Creating new recipe: {recipe_data['name']}")
                db_recipe = Recipe(
                    id=recipe_id,
                    name=recipe_data['name'],
                    servings=recipe_data.get('servings'),
                    photo_path=recipe_data.get('photo_path')
                )
                session.add(db_recipe)

            for ing_data in recipe_data.get('ingredients', []):
                new_ingredient = Ingredient(
                    name=ing_data['name'],
                    amount=ing_data['amount'],
                    group_name=ing_data.get('group_name'),
                    is_optional=ing_data.get('is_optional', False),
                    order_index=ing_data['order_index']
                )
                db_recipe.ingredients.append(new_ingredient)

            for inst_data in recipe_data.get('instructions', []):
                new_instruction = Instruction(
                    step_number=inst_data['step_number'],
                    description=inst_data['description']
                )
                db_recipe.instructions.append(new_instruction)

            for note_data in recipe_data.get('notes', []):
                new_note = Note(
                    name=note_data['name'],
                    text=note_data['text']
                )
                db_recipe.notes.append(new_note)

            for tag_name in recipe_data.get('tags', []):
                tag_name = tag_name.strip()
                if not tag_name:
                    continue
                
                db_tag = tags_map.get(tag_name)
                if not db_tag:
                    db_tag = Tag(name=tag_name)
                    session.add(db_tag)
                    tags_map[tag_name] = db_tag
                
                recipe_tag_assoc = RecipeTag(tag=db_tag)
                db_recipe.recipe_tags.append(recipe_tag_assoc)

        session.commit()
        print("Import complete.")

    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Imports recipes from a JSON backup file, updating existing recipes and creating new ones.",
        epilog="This script is designed to work with JSON files created by export_recipes.py."
    )
    parser.add_argument("file_path", help="The path to the JSON backup file to import.")
    args = parser.parse_args()
    
    import_recipes(args.file_path)