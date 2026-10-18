from app import crud, schemas


def test_html_pages_render(client, db_session):
    recipe = crud.create_recipe(
        db=db_session,
        recipe=schemas.RecipeCreate(
            name="Tomato Soup", servings="4", tags=["soup"], ingredients=[], instructions=[], notes=[]
        ),
    )

    for path in ["/", "/?search=Tomato", "/recipe/new", f"/recipe/{recipe.id}", "/tag/soup"]:
        response = client.get(path)
        assert response.status_code == 200, path
        assert "Tomato Soup" in response.text or path == "/recipe/new", path


def test_ingredient_group_heading_is_shown_once_per_group(client, db_session):
    ingredients = [
        schemas.IngredientCreate(name="Flour", amount="200g", order_index=0, group_name="For the dough"),
        schemas.IngredientCreate(name="Water", amount="100ml", order_index=1, group_name="For the dough"),
        schemas.IngredientCreate(name="Tomato", amount="2", order_index=2, group_name="For the sauce"),
        schemas.IngredientCreate(name="Basil", amount="1", order_index=3, group_name="For the sauce"),
    ]
    recipe = crud.create_recipe(db=db_session, recipe=schemas.RecipeCreate(name="Pizza", ingredients=ingredients))

    html = client.get(f"/recipe/{recipe.id}").text

    assert html.count("<strong>For the dough</strong>") == 1
    assert html.count("<strong>For the sauce</strong>") == 1
    assert html.index("For the dough") < html.index("Flour") < html.index("For the sauce") < html.index("Tomato")
