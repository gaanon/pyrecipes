import json
import os
import sys
from sqlalchemy.orm import sessionmaker, joinedload
from app.database import engine
from app.models import Recipe, RecipeTag

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def export_recipes():
    """
    Reads recipes from the database and exports them to a JSON file.
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Exporting recipes...")

    # Eagerly load related data to avoid N+1 query problems
    recipes = session.query(Recipe).options(
        joinedload(Recipe.ingredients),
        joinedload(Recipe.instructions),
        joinedload(Recipe.notes),
        joinedload(Recipe.recipe_tags).joinedload(RecipeTag.tag)
    ).all()

    output_data = {
        "recipes": [],
    }

    for recipe in recipes:
        recipe_data = {
            "id": recipe.id,
            "name": recipe.name,
            "servings": recipe.servings,
            "photo_path": recipe.photo_path,
            "tags": [rt.tag.name for rt in recipe.recipe_tags],
            "ingredients": [
                {
                    "id": ing.id,
                    "name": ing.name,
                    "amount": ing.amount,
                    "group_name": ing.group_name,
                    "is_optional": ing.is_optional,
                    "order_index": ing.order_index
                } for ing in sorted(recipe.ingredients, key=lambda x: x.order_index)
            ],
            "instructions": [
                {
                    "id": inst.id,
                    "step_number": inst.step_number,
                    "description": inst.description
                } for inst in sorted(recipe.instructions, key=lambda x: x.step_number)
            ],
            "notes": [
                {
                    "id": note.id,
                    "name": note.name,
                    "text": note.text
                } for note in recipe.notes
            ]
        }
        output_data["recipes"].append(recipe_data)

    # Write the data to a JSON file
    with open('backups/recipes_export.json', 'w') as f:
        json.dump(output_data, f, indent=4)

    session.close()
    print("Export complete.")

if __name__ == "__main__":
    export_recipes()