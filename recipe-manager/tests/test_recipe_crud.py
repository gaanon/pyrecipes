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
    keep = models.MealPlan(plan_date=datetime.date(2026, 10, 20), custom_meal_name="Keep")
    remove = models.MealPlan(plan_date=datetime.date(2026, 10, 21), custom_meal_name="Remove")
    db_session.add_all([keep, remove])
    db_session.commit()

    response = client.delete(f"/api/meal-plan/{remove.id}")

    assert response.status_code == 200
    db_session.expire_all()
    assert [m.custom_meal_name for m in db_session.query(models.MealPlan).all()] == ["Keep"]


def test_deleting_a_planned_recipe_keeps_the_meal_by_name(client, db_session):
    recipe = _create_recipe(db_session)
    db_session.add(models.MealPlan(plan_date=datetime.date(2026, 10, 20), recipe_id=recipe.id))
    db_session.commit()

    response = client.post(f"/recipe/{recipe.id}/delete", follow_redirects=False)

    assert response.status_code == 303
    meals = client.get("/api/meal-plan", params={"start_date": "2026-10-19", "end_date": "2026-10-25"}).json()
    assert [(m["recipe_id"], m["recipe"], m["custom_meal_name"]) for m in meals] == [(None, None, "Tomato Soup")]


def test_ingredients_and_steps_come_back_in_order(db_session):
    recipe = _create_recipe(
        db_session,
        ingredients=[
            schemas.IngredientCreate(name="Third", amount="1", order_index=2),
            schemas.IngredientCreate(name="First", amount="1", order_index=0),
            schemas.IngredientCreate(name="Second", amount="1", order_index=1),
        ],
        instructions=[
            schemas.InstructionCreate(step_number=2, description="Second"),
            schemas.InstructionCreate(step_number=1, description="First"),
        ],
    )

    db_session.expire_all()
    saved = crud.get_recipe(db_session, recipe_id=recipe.id)

    assert [i.name for i in saved.ingredients] == ["First", "Second", "Third"]
    assert [s.description for s in saved.instructions] == ["First", "Second"]


def test_repeated_tags_are_saved_once_ignoring_case(client, db_session):
    _create_recipe(db_session, name="Existing", tags=["Dinner"])

    response = client.post(
        "/recipe/new",
        data={"name": "Pasta", "tags": "Quick, quick, Dinner, dinner, Quick, , "},
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.expire_all()
    pasta = db_session.query(models.Recipe).filter_by(name="Pasta").one()
    # Existing tags keep their spelling; the first spelling of a new tag wins
    assert sorted(rt.tag.name for rt in pasta.recipe_tags) == ["Dinner", "Quick"]
    assert sorted(t.name for t in db_session.query(models.Tag).all()) == ["Dinner", "Quick"]
