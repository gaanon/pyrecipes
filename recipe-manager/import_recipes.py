import argparse
import datetime
import json
import sys

from pydantic import ValidationError
from sqlalchemy import delete
from sqlalchemy.orm import sessionmaker

from app import crud, schemas
from app.database import engine
from app.models import MealPlan, Recipe


class RecipeImportError(Exception):
    pass


def import_recipes(file_path, session):
    """Restores recipes (and the meal plan, if present) from a backup_app.py JSON export.

    Recipes are matched by id: existing ones are updated, missing ones created. A meal plan in
    the file replaces the current one. Everything is saved in one transaction, so a bad file
    changes nothing. Raises RecipeImportError on invalid data.
    """
    print(f"Importing recipes from {file_path}...")
    with open(file_path) as f:
        data = json.load(f)

    try:
        for recipe_data in data["recipes"]:
            name = recipe_data.get("name", "<no name>")
            try:
                recipe = schemas.RecipeCreate.model_validate(recipe_data)
            except ValidationError as e:
                raise RecipeImportError(f"Recipe {recipe_data.get('id')} ({name!r}) is invalid: {e}")

            db_recipe = session.get(Recipe, recipe_data["id"]) if recipe_data.get("id") else None
            if db_recipe:
                print(f"Updating recipe: {name}")
            else:
                print(f"Creating new recipe: {name}")
                db_recipe = Recipe(id=recipe_data.get("id"))
                session.add(db_recipe)
            # Same rules as saving from the app: case-insensitive tags, each linked once
            crud._apply_recipe(session, db_recipe, recipe)
            db_recipe.photo_path = recipe_data.get("photo_path")
            session.flush()

        if "meal_plans" in data:
            session.execute(delete(MealPlan))
            for meal in data["meal_plans"]:
                session.add(MealPlan(
                    id=meal.get("id"),
                    plan_date=datetime.date.fromisoformat(meal["plan_date"]),
                    recipe_id=meal.get("recipe_id"),
                    custom_meal_name=meal.get("custom_meal_name"),
                ))
        session.commit()
    except Exception:
        session.rollback()
        raise
    print(f"Import complete: {len(data['recipes'])} recipes, {len(data.get('meal_plans', []))} planned meals.")


def main(argv=None, session_factory=None):
    parser = argparse.ArgumentParser(
        description="Imports recipes from a JSON backup file, updating existing recipes and creating new ones.",
        epilog="Reads the recipes_export.json written by backup_app.py.",
    )
    parser.add_argument("file_path", help="The path to the JSON backup file to import.")
    args = parser.parse_args(argv)

    session = (session_factory or sessionmaker(bind=engine, autoflush=False))()
    try:
        import_recipes(args.file_path, session)
    except Exception as e:
        print(f"Import FAILED, nothing was changed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
