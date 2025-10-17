import json
import os
import sys
import re
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import Base, Recipe, Ingredient, Instruction

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def parse_instructions(method_text):
    """
    Parses the method text to extract a list of instructions.
    """
    if not method_text:
        return []
    # Find all numbered steps
    steps = re.findall(r'\d+\.\s*(.*?)(?=\s*\d+\.|$)', method_text, re.DOTALL)
    if not steps:
        # If no numbered steps, split by newline
        steps = [s.strip() for s in method_text.split('\n') if s.strip()]
        if len(steps) > 1:
             return steps
        else: # if only one line or no lines, return as is if not empty
            return [method_text.strip()] if method_text.strip() else []

    return [step.strip().replace('\r\n', ' ').replace('\n', ' ') for step in steps if step.strip()]

def parse_ingredient_string(full_ingredient_name):
    """
    Parses a full ingredient string like "100g sugar" into an amount and a name.
    """
    # This regex tries to capture a leading amount/unit part.
    match = re.match(r'((?:[\d\s/.\u00BC-\u00BE\u2150-\u215E]+)?\s*(?:g|kg|ml|l|tbsp|tsp|cup|can|cans|clove|cloves|diente|dientes|tacitas|muslos|cucharadas|pizca|litro|hebras|gr|grams|gram|pack)?)?\s*(.*)', full_ingredient_name.strip())
    if match:
        amount = match.group(1).strip() if match.group(1) else ""
        name = match.group(2).strip()
        if not amount and re.match(r'^\d', name): # case where amount was not captured because unit was missing
             parts = name.split(' ', 1)
             if len(parts) > 1:
                 amount = parts[0]
                 name = parts[1]

        return amount, name
    return "", full_ingredient_name

def import_recipes():
    """
    Reads recipes from a JSON file and imports them into the database.
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    # Ensure the app directory is in the Python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

    # Load the JSON data
    with open('gorecipes_export.json', 'r') as f:
        data = json.load(f)

    # Create lookups for ingredients
    ingredients_map = {ing['id']: ing['name'] for ing in data.get('ingredients', [])}
    recipe_ingredients_map = {}
    for ri in data.get('recipe_ingredients', []):
        recipe_id = ri['recipe_id']
        if recipe_id not in recipe_ingredients_map:
            recipe_ingredients_map[recipe_id] = []
        recipe_ingredients_map[recipe_id].append(ri['ingredient_id'])


    print("Importing recipes...")

    for recipe_data in data['recipes']:
        recipe_name = recipe_data.get('name')
        method = recipe_data.get('method')
        recipe_id_json = recipe_data.get('id')

        if not recipe_name:
            continue

        print(f"Processing recipe: {recipe_name}")

        # Create a new recipe object
        new_recipe = Recipe(
            name=recipe_name,
            photo_path=recipe_data.get('photo_filename')
        )

        # Parse and add instructions
        if method:
            instructions = parse_instructions(method)
            for i, instruction_text in enumerate(instructions):
                new_instruction = Instruction(step_number=i + 1, description=instruction_text)
                new_recipe.instructions.append(new_instruction)

        # Get ingredients for this recipe
        ingredient_ids = recipe_ingredients_map.get(recipe_id_json, [])
        for i, ing_id in enumerate(ingredient_ids):
            full_ingredient_name = ingredients_map.get(ing_id)
            if full_ingredient_name:
                amount, name = parse_ingredient_string(full_ingredient_name)
                new_ingredient = Ingredient(
                    name=name,
                    amount=amount,
                    order_index=i
                )
                new_recipe.ingredients.append(new_ingredient)

        session.add(new_recipe)

    # Commit the changes to the database
    try:
        session.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        # Close the session
        session.close()
    
    print("Import complete.")

if __name__ == "__main__":
    import_recipes()