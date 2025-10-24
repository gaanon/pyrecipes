import os
import base64
import json
from openai import OpenAI
from . import schemas
from fastapi import UploadFile

# It's a good practice to load the API key from environment variables
# Make sure to set your OPENAI_API_KEY in your environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_recipe_json_prompt():
    return """
    You are a recipe parsing assistant. Analyze the provided image of a recipe and extract the information into a structured JSON object.

    The JSON object must follow this exact format:
    {
      "name": "The name of the recipe",
      "servings": "The servings or yield (e.g., '4 people', '12 muffins')",
      "ingredients": [
        {
          "group_name": "Optional group name (e.g., 'For the filling')",
          "name": "Name of the ingredient",
          "amount": "Quantity of the ingredient (e.g., '1 cup', '200g')",
          "is_optional": false,
          "order_index": 0
        }
      ],
      "instructions": [
        {
          "step_number": 1,
          "description": "The first step of the instructions."
        }
      ],
      "notes": [
        {
            "name": "Title of the note",
            "text": "Content of the note"
        }
      ],
      "tags": ["tag1", "tag2", "tag3"]
    }

    Based on the recipe content, you must also generate relevant tags. Include tags for:
    - Meal type (e.g., 'breakfast', 'lunch', 'dinner', 'dessert')
    - Main ingredient (e.g., 'chicken', 'beef', 'pasta', 'chocolate')
    - Dish category (e.g., 'soup', 'salad', 'main course', 'baking')

    Important Rules:
    - If a value is not present in the image (e.g., no notes, no servings), omit the field or set it to an empty list/string.
    - Do not include any fields that are not in the provided JSON structure.
    - Pay close attention to ingredient groups. If ingredients are listed under a sub-heading, use that as the `group_name`.
    - Ensure `order_index` for ingredients and `step_number` for instructions are sequential and start from 0 and 1 respectively.
    - The final output must be a single, valid JSON object and nothing else. Do not include any explanatory text before or after the JSON.
    """

async def extract_recipe_from_image(image_file: UploadFile) -> schemas.RecipeCreate:
    """
    This function takes an image file, sends it to the GPT-4 Vision API,
    and returns a structured RecipeCreate object.
    """
    image_data = await image_file.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')

    prompt_text = get_recipe_json_prompt()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2048,
        )

        # Extract the JSON content from the response
        json_string = response.choices[0].message.content
        # Clean up the string in case the model returns it wrapped in markdown
        if json_string.startswith("```json"):
            json_string = json_string[7:-4]
        
        recipe_dict = json.loads(json_string)
        
        # Ensure ingredients and instructions have correct indexing if missing
        for i, ing in enumerate(recipe_dict.get("ingredients", [])):
            ing['order_index'] = i
        for i, inst in enumerate(recipe_dict.get("instructions", [])):
            inst['step_number'] = i + 1

        return schemas.RecipeCreate(**recipe_dict)

    except Exception as e:
        print(f"An error occurred with the OpenAI API call: {e}")
        # Return an empty or default schema on error
        return schemas.RecipeCreate(name="Error: Could not parse recipe", ingredients=[], instructions=[], tags=[])