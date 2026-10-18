"""Missing records give 404 and bad input gives 422, instead of server errors."""
import json

import pytest

from app import models


@pytest.mark.parametrize("method, path", [
    ("get", "/recipe/999"),
    ("get", "/recipe/999/edit"),
    ("post", "/recipe/999/delete"),
    ("delete", "/api/meal-plan/999"),
])
def test_missing_records_are_404(client_500, method, path):
    assert getattr(client_500, method)(path).status_code == 404


def test_editing_a_missing_recipe_is_404(client_500):
    response = client_500.post("/recipe/999/edit", data={"name": "Ghost"})

    assert response.status_code == 404


@pytest.mark.parametrize("ingredients", [
    "not json",
    json.dumps([{"name": "Tomato"}]),  # amount and order_index missing
    json.dumps({"name": "Tomato"}),     # an object, not a list
])
def test_malformed_recipe_form_is_422_and_saves_nothing(client_500, db_session, ingredients):
    response = client_500.post("/recipe/new", data={"name": "Soup", "ingredients": ingredients})

    assert response.status_code == 422
    assert db_session.query(models.Recipe).count() == 0


@pytest.mark.parametrize("payload", [
    {"plan_date": "2026-10-20", "recipe_id": 999},  # recipe doesn't exist
    {"plan_date": "2026-10-20"},                     # neither a recipe nor a custom meal
])
def test_invalid_meal_plan_entry_is_422(client_500, db_session, payload):
    response = client_500.post("/api/meal-plan", json=payload)

    assert response.status_code == 422
    assert db_session.query(models.MealPlan).count() == 0
