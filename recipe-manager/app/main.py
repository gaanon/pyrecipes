from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models, database, schemas

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db), search: str = None):
    from . import crud
    if search:
        recipes = crud.search_recipes(db=db, query=search)
    else:
        recipes = crud.get_recipes(db=db)
    return templates.TemplateResponse("index.html", {"request": request, "recipes": recipes, "search": search})

@app.get("/recipe/new", response_class=HTMLResponse)
async def new_recipe_form(request: Request):
    return templates.TemplateResponse("recipe_form.html", {"request": request, "recipe": None})

@app.get("/recipe/{id}", response_class=HTMLResponse)
async def recipe_detail(request: Request, id: int, db: Session = Depends(get_db)):
    from . import crud
    recipe = crud.get_recipe(db, recipe_id=id)
    return templates.TemplateResponse("recipe_detail.html", {"request": request, "recipe": recipe})

@app.post("/recipe/new", response_class=HTMLResponse)
async def create_recipe(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    
    # Handle file upload
    photo_path = None
    photo = form.get("photo")
    if photo and photo.filename:
        # You would add logic here to save the file and get the path
        # For now, we'll just simulate it
        photo_path = f"uploads/{photo.filename}"
        with open(f"app/static/{photo_path}", "wb") as buffer:
            buffer.write(await photo.read())

    # Create recipe schema
    # Process ingredients manually
    ingredients = []
    ingredient_names = form.getlist("ingredient_name")
    ingredient_groups = form.getlist("ingredient_group")
    ingredient_amounts = form.getlist("ingredient_amount")
    ingredient_optionals = form.getlist("ingredient_optional")

    for i, name in enumerate(ingredient_names):
        ingredients.append(schemas.IngredientCreate(
            group_name=ingredient_groups[i],
            name=name,
            amount=ingredient_amounts[i],
            is_optional=str(i) in ingredient_optionals,
            order_index=i
        ))

    recipe_data = schemas.RecipeCreate(
        name=form.get("name"),
        servings=form.get("servings"),
        ingredients=ingredients,
        instructions=[
            schemas.InstructionCreate(step_number=i + 1, description=desc)
            for i, desc in enumerate(form.getlist("instruction_description"))
        ],
        notes=[
            schemas.NoteCreate(name=name, text=text)
            for name, text in zip(form.getlist("note_name"), form.getlist("note_text"))
            if name and text
        ],
        tags=form.get("tags").split(",") if form.get("tags") else []
    )

    # Create recipe in DB
    from . import crud
    db_recipe = crud.create_recipe(db=db, recipe=recipe_data)
    
    # Update photo path if it exists
    if photo_path:
        db_recipe.photo_path = photo_path
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)

    # Redirect to the main page
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=303)

@app.get("/recipe/{id}/edit", response_class=HTMLResponse)
async def edit_recipe_form(request: Request, id: int, db: Session = Depends(get_db)):
    from . import crud
    recipe = crud.get_recipe(db, recipe_id=id)
    return templates.TemplateResponse("recipe_form.html", {"request": request, "recipe": recipe})

@app.post("/recipe/{id}/edit", response_class=HTMLResponse)
async def edit_recipe(request: Request, id: int, db: Session = Depends(get_db)):
    form = await request.form()
    
    # Handle file upload
    photo_path = None
    photo = form.get("photo")
    if photo and photo.filename:
        # You would add logic here to save the file and get the path
        # For now, we'll just simulate it
        photo_path = f"uploads/{photo.filename}"
        with open(f"app/static/{photo_path}", "wb") as buffer:
            buffer.write(await photo.read())

    # Create recipe schema
    # Process ingredients manually
    ingredients = []
    ingredient_names = form.getlist("ingredient_name")
    ingredient_groups = form.getlist("ingredient_group")
    ingredient_amounts = form.getlist("ingredient_amount")
    ingredient_optionals = form.getlist("ingredient_optional")

    for i, name in enumerate(ingredient_names):
        ingredients.append(schemas.IngredientCreate(
            group_name=ingredient_groups[i],
            name=name,
            amount=ingredient_amounts[i],
            is_optional=str(i) in ingredient_optionals,
            order_index=i
        ))

    recipe_data = schemas.RecipeCreate(
        name=form.get("name"),
        servings=form.get("servings"),
        ingredients=ingredients,
        instructions=[
            schemas.InstructionCreate(step_number=i + 1, description=desc)
            for i, desc in enumerate(form.getlist("instruction_description"))
        ],
        notes=[
            schemas.NoteCreate(name=name, text=text)
            for name, text in zip(form.getlist("note_name"), form.getlist("note_text"))
            if name and text
        ],
        tags=form.get("tags").split(",") if form.get("tags") else []
    )

    # Update recipe in DB
    from . import crud
    db_recipe = crud.update_recipe(db=db, recipe_id=id, recipe=recipe_data)
    
    # Update photo path if it exists
    if photo_path:
        db_recipe.photo_path = photo_path
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)

    # Redirect to the recipe detail page
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/recipe/{id}", status_code=303)

@app.post("/recipe/{id}/delete", response_class=HTMLResponse)
async def delete_recipe(request: Request, id: int, db: Session = Depends(get_db)):
    from . import crud
    crud.delete_recipe(db=db, recipe_id=id)
    return RedirectResponse(url="/", status_code=303)

@app.get("/tag/{tag_name}", response_class=HTMLResponse)
async def view_recipes_by_tag(request: Request, tag_name: str, db: Session = Depends(get_db)):
    from . import crud
    recipes = crud.get_recipes_by_tag(db=db, tag_name=tag_name)
    return templates.TemplateResponse("index.html", {"request": request, "recipes": recipes, "tag_name": tag_name})