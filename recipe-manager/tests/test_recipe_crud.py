import datetime
import json

from app import crud, models, schemas


def _create_recipe(db, **overrides):
    fields = dict(name="Tomato Soup", servings="4", tags=["soup"], ingredients=[], instructions=[], notes=[])
    fields.update(overrides)
    return crud.create_recipe(db=db, recipe=schemas.RecipeCreate(**fields))


def test_edit_replaces_ingredients_instructions_and_notes(client, db_session):
    recipe = _create_recipe(
        db_session,
        ingredients=[schemas.IngredientCreate(name="Old tomato", amount="1", order_index=0)],
        instructions=[schemas.InstructionCreate(step_number=1, description="Old step")],
        notes=[schemas.NoteCreate(name="Old", text="Old note")],
    )

    response = client.post(
        f"/recipe/{recipe.id}/edit",
        data={
            "name": "Better Soup",
            "servings": "2",
            "tags": "soup",
            "ingredients": json.dumps([
                {"name": "Tomato", "amount": "6", "order_index": 0},
                {"name": "Basil", "amount": "1 bunch", "order_index": 1, "group_name": "Garnish"},
            ]),
            "instructions": json.dumps([{"step_number": 1, "description": "Simmer."}]),
            "notes": json.dumps([]),
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.expire_all()
    saved = crud.get_recipe(db_session, recipe_id=recipe.id)
    assert (saved.name, saved.servings) == ("Better Soup", "2")
    assert sorted((i.name, i.amount, i.group_name) for i in saved.ingredients) == [
        ("Basil", "1 bunch", "Garnish"),
        ("Tomato", "6", None),
    ]
    assert [s.description for s in saved.instructions] == ["Simmer."]
    assert saved.notes == []
    assert db_session.query(models.Ingredient).count() == 2


def test_delete_recipe_removes_it_and_its_children(client, db_session):
    recipe = _create_recipe(
        db_session, ingredients=[schemas.IngredientCreate(name="Tomato", amount="1", order_index=0)]
    )

    response = client.post(f"/recipe/{recipe.id}/delete", follow_redirects=False)

    assert response.status_code == 303
    db_session.expire_all()
    assert crud.get_recipe(db_session, recipe_id=recipe.id) is None
    assert db_session.query(models.Ingredient).count() == 0
    assert db_session.query(models.RecipeTag).count() == 0


def test_delete_meal_plan_entry(client, db_session):
    keep = models.MealPlan(plan_date=datetime.datetime(2026, 10, 20), custom_meal_name="Keep")
    remove = models.MealPlan(plan_date=datetime.datetime(2026, 10, 21), custom_meal_name="Remove")
    db_session.add_all([keep, remove])
    db_session.commit()

    response = client.delete(f"/api/meal-plan/{remove.id}")

    assert response.status_code == 200
    db_session.expire_all()
    assert [m.custom_meal_name for m in db_session.query(models.MealPlan).all()] == ["Keep"]
