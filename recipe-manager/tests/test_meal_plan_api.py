import datetime

from app import models


def test_get_meal_plan_returns_meals_in_range_with_recipe(client, db_session):
    recipe = models.Recipe(name="Tomato Soup", servings="4")
    db_session.add_all([
        models.MealPlan(plan_date=datetime.datetime(2026, 10, 20), recipe=recipe),
        models.MealPlan(plan_date=datetime.datetime(2026, 10, 21), custom_meal_name="Leftovers"),
        models.MealPlan(plan_date=datetime.datetime(2026, 11, 5), custom_meal_name="Out of range"),
    ])
    db_session.commit()

    response = client.get("/api/meal-plan", params={"start_date": "2026-10-19", "end_date": "2026-10-25"})

    assert response.status_code == 200
    meals = sorted(response.json(), key=lambda m: m["plan_date"])
    assert [(m["plan_date"], m["custom_meal_name"]) for m in meals] == [
        ("2026-10-20", None),
        ("2026-10-21", "Leftovers"),
    ]
    assert meals[0]["recipe"]["name"] == "Tomato Soup"
    assert meals[1]["recipe"] is None
