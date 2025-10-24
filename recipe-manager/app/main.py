from fastapi import FastAPI, Depends, Request, File, UploadFile
from typing import List
import datetime
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models, database, schemas, ai_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the database tables on startup
    models.Base.metadata.create_all(bind=database.engine)
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

from . import utils

templates = Jinja2Templates(directory="app/templates")
templates.env.globals['get_color_from_string'] = utils.get_color_from_string

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

@app.post("/api/process-recipe-image", response_model=schemas.RecipeCreate)
async def process_recipe_image(file: UploadFile = File(...)):
    recipe_data = await ai_service.extract_recipe_from_image(file)
    return recipe_data

@app.get("/recipe/new", response_class=HTMLResponse)
async def new_recipe_form(request: Request):
    return templates.TemplateResponse("recipe_form.html", {"request": request, "recipe": None})

@app.get("/recipe/{id}", response_class=HTMLResponse)
async def recipe_detail(request: Request, id: int, db: Session = Depends(get_db)):
    from . import crud
    recipe = crud.get_recipe(db, recipe_id=id)
    return templates.TemplateResponse("recipe_detail.html", {"request": request, "recipe": recipe})

@app.post("/recipe/new", response_model=schemas.Recipe)
async def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    from . import crud
    db_recipe = crud.create_recipe(db=db, recipe=recipe)
    return db_recipe

@app.get("/recipe/{id}/edit", response_class=HTMLResponse)
async def edit_recipe_form(request: Request, id: int, db: Session = Depends(get_db)):
    from . import crud
    recipe = crud.get_recipe(db, recipe_id=id)
    return templates.TemplateResponse("recipe_form.html", {"request": request, "recipe": recipe})

@app.post("/recipe/{id}/edit", response_model=schemas.Recipe)
async def edit_recipe(id: int, recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    from . import crud
    db_recipe = crud.update_recipe(db=db, recipe_id=id, recipe=recipe)
    return db_recipe

@app.post("/recipe/{id}/delete", response_class=HTMLResponse)
async def delete_recipe(request: Request, id: int, db: Session = Depends(get_db)):
    from . import crud
    crud.delete_recipe(db=db, recipe_id=id)
    return RedirectResponse(url="/", status_code=303)

# API endpoints for Meal Planner
@app.get("/api/meal-plan", response_model=List[schemas.MealPlan])
def get_meal_plan_for_week(start_date: datetime.date, end_date: datetime.date, db: Session = Depends(get_db)):
    from . import crud
    return crud.get_meal_plans(db, start_date=start_date, end_date=end_date)

@app.post("/api/meal-plan", response_model=schemas.MealPlan)
def add_meal_to_plan(meal_plan: schemas.MealPlanCreate, db: Session = Depends(get_db)):
    from . import crud
    return crud.create_meal_plan(db=db, meal_plan=meal_plan)

@app.delete("/api/meal-plan/{meal_plan_id}")
def delete_meal_from_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    from . import crud
    crud.delete_meal_plan(db=db, meal_plan_id=meal_plan_id)
    return {"ok": True}

@app.get("/tag/{tag_name}", response_class=HTMLResponse)
async def view_recipes_by_tag(request: Request, tag_name: str, db: Session = Depends(get_db)):
    from . import crud
    recipes = crud.get_recipes_by_tag(db=db, tag_name=tag_name)
    return templates.TemplateResponse("index.html", {"request": request, "recipes": recipes, "tag_name": tag_name})