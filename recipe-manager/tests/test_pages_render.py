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
