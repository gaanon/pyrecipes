import base64
import json
import logging
import os
import re
from typing import Optional

import httpx2
import openai
from fastapi import UploadFile
from pydantic import ValidationError

from . import schemas

logger = logging.getLogger(__name__)

# Vision calls can be slow; give up after this many seconds rather than hang the request
AI_TIMEOUT_SECONDS = float(os.environ.get("AI_TIMEOUT_SECONDS") or 60)


class AIServiceError(Exception):
    """The AI provider failed or returned something unusable; `status_code` is the HTTP status to report."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def _get_client(http_client: Optional[httpx2.AsyncClient] = None) -> openai.AsyncOpenAI:
    return openai.AsyncOpenAI(
        api_key=os.environ.get("AI_API_KEY") or os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("AI_API_BASE_URL") or None,  # None: the default OpenAI endpoint
        timeout=AI_TIMEOUT_SECONDS,
        max_retries=1,
        http_client=http_client,
    )


def _root_cause(error: BaseException) -> str:
    """The innermost exception as "Type: message"; network errors often have an empty message."""
    while error.__cause__ is not None:
        error = error.__cause__
    return f"{type(error).__name__}: {error}".rstrip(": ")


def _get_model() -> str:
    return os.environ.get("AI_MODEL") or "gpt-4o-mini"

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

def _answer_text(response, model: str, image: str) -> Optional[str]:
    """The answer's text; if there is none, raises AIServiceError saying why (refusal, token limit...)."""
    if not response.choices:
        raise AIServiceError("The AI returned no answer")
    choice = response.choices[0]
    if choice.message.content:
        return choice.message.content
    refusal = getattr(choice.message, "refusal", None)
    logger.warning("AI returned no text (model=%s, image=%s, finish_reason=%s, refusal=%r, usage=%s)",
                   model, image, choice.finish_reason, refusal, response.usage)
    if refusal:
        raise AIServiceError(f"The AI declined to read the image: {refusal}")
    if choice.finish_reason == "length":
        raise AIServiceError("The AI hit its token limit before writing the recipe (finish_reason=length)")
    raise AIServiceError(f"The AI returned an empty answer (finish_reason={choice.finish_reason})")


def _extract_json(content: Optional[str]) -> dict:
    """Finds the JSON object in the model's answer, which may be wrapped in a Markdown fence or prose."""
    if not content:
        raise AIServiceError("The AI returned an empty answer")
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
    candidate = fenced.group(1) if fenced else content[content.find("{"):content.rfind("}") + 1]
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        raise AIServiceError("The AI's answer did not contain a readable recipe")
    if not isinstance(data, dict):
        raise AIServiceError("The AI's answer did not contain a readable recipe")
    return data


async def extract_recipe_from_image(image_file: UploadFile) -> schemas.RecipeCreate:
    """Sends the image to the configured OpenAI-compatible vision model and returns the recipe it reads.

    Raises AIServiceError if the provider fails, times out, or returns something that isn't a recipe.
    """
    image_data = await image_file.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')
    content_type = image_file.content_type or "image/jpeg"
    model = _get_model()

    try:
        response = await _get_client().chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": get_recipe_json_prompt()},
                        {"type": "image_url", "image_url": {"url": f"data:{content_type};base64,{base64_image}"}},
                    ],
                }
            ],
            max_tokens=2048,
        )
    except openai.APITimeoutError:
        logger.warning("AI request timed out after %ss (model=%s)", AI_TIMEOUT_SECONDS, model)
        raise AIServiceError("The AI took too long to answer", status_code=504)
    except openai.APIStatusError as e:
        logger.error("AI provider returned HTTP %s (model=%s, base_url=%s): %s",
                     e.status_code, model, os.environ.get("AI_API_BASE_URL") or "default", e.message)
        raise AIServiceError(f"The AI provider returned HTTP {e.status_code}")
    except openai.APIConnectionError as e:
        logger.error("Could not reach the AI provider at %s (model=%s): %s",
                     os.environ.get("AI_API_BASE_URL") or "default", model, _root_cause(e))
        raise AIServiceError(f"Could not reach the AI provider: {e}")
    except openai.OpenAIError as e:
        logger.exception("AI request failed (model=%s)", model)
        raise AIServiceError(f"Could not reach the AI provider: {e}")

    recipe_dict = _extract_json(_answer_text(response, model, f"{content_type}, {len(image_data)} bytes"))

    # Number ingredients and steps in the order the model listed them
    for i, ing in enumerate(recipe_dict.get("ingredients") or []):
        if isinstance(ing, dict):
            ing['order_index'] = i
    for i, inst in enumerate(recipe_dict.get("instructions") or []):
        if isinstance(inst, dict):
            inst['step_number'] = i + 1

    try:
        return schemas.RecipeCreate.model_validate(recipe_dict)
    except ValidationError as e:
        logger.warning("AI answer was not a valid recipe: %s", e)
        raise AIServiceError("The AI's answer was not a valid recipe")
