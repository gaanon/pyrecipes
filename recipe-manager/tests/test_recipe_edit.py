import re

from app import crud, schemas


def _create_recipe(db, tags):
    return crud.create_recipe(
        db=db,
        recipe=schemas.RecipeCreate(
            name="Tomato Soup",
            servings="4",
            tags=tags,
            ingredients=[],
            instructions=[],
            notes=[],
        ),
    )


def _tags_field_value(html):
    match = re.search(r'<input[^>]*id="tags"[^>]*value="([^"]*)"', html)
    assert match, "tags input not found on the edit form"
    return match.group(1)


def test_edit_form_prefills_existing_tags(client, db_session):
    recipe = _create_recipe(db_session, ["soup", "dinner"])

    response = client.get(f"/recipe/{recipe.id}/edit")

    assert response.status_code == 200
    assert sorted(t.strip() for t in _tags_field_value(response.text).split(",")) == ["dinner", "soup"]


def test_saving_edit_form_unchanged_keeps_tags(client, db_session):
    recipe = _create_recipe(db_session, ["soup", "dinner"])
    tags_on_form = _tags_field_value(client.get(f"/recipe/{recipe.id}/edit").text)

    response = client.post(
        f"/recipe/{recipe.id}/edit",
        data={"name": "Tomato Soup", "servings": "4", "tags": tags_on_form},
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.expire_all()
    saved = crud.get_recipe(db_session, recipe_id=recipe.id)
    assert sorted(rt.tag.name for rt in saved.recipe_tags) == ["dinner", "soup"]
