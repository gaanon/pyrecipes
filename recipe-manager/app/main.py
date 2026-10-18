from fastapi import FastAPI, Depends, HTTPException, Request, File, UploadFile, Form
from fastapi.exceptions import RequestValidationError
from typing import List, Optional
import datetime
import json
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session
from . import models, crud, database, schemas, ai_service, db_migrate, utils
from .database import get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create or upgrade the database schema on startup
    db_migrate.run_migrations(database.engine)
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory=crud.UPLOAD_DIR), name="uploads")

templates = Jinja2Templates(directory="app/templates")
templates.env.globals['get_color_from_string'] = utils.get_color_from_string


def _get_recipe_or_404(db: Session, recipe_id: int) -> models.Recipe:
    recipe = crud.get_recipe(db, recipe_id=recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


def recipe_form(
    name: str = Form(...),
    servings: str = Form(""),
    tags: str = Form(""),
    ingredients: str = Form("[]"),
    instructions: str = Form("[]"),
    notes: str = Form("[]"),
) -> schemas.RecipeCreate:
    """Parses the recipe form; the list fields arrive as JSON strings serialized by the page's JS."""
    lists = {}
    for field, raw in (("ingredients", ingredients), ("instructions", instructions), ("notes", notes)):
        try:
            lists[field] = json.loads(raw)
        except json.JSONDecodeError as e:
            raise RequestValidationError([{"type": "json_invalid", "loc": ("body", field), "msg": str(e), "input": raw}])
    try:
        return schemas.RecipeCreate.model_validate({
            "name": name,
            "servings": servings,
            "tags": [tag.strip() for tag in tags.split(',') if tag.strip()],
            **lists,
        })
    except ValidationError as e:
        raise RequestValidationError(e.errors(include_url=False))


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db), search: str = None):
    if search:
        recipes = crud.search_recipes(db=db, query=search)
    else:
        recipes = crud.get_recipes(db=db)
    return templates.TemplateResponse(request, "index.html", {"recipes": recipes, "search": search})

@app.post("/api/process-recipe-image", response_model=schemas.RecipeCreate)
async def process_recipe_image(file: UploadFile = File(...)):
    try:
        return await ai_service.extract_recipe_from_image(file)
    except ai_service.AIServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

@app.get("/recipe/new", response_class=HTMLResponse)
async def new_recipe_form(request: Request):
    return templates.TemplateResponse(request, "recipe_form.html", {"recipe": None})

@app.get("/recipe/{id}", response_class=HTMLResponse)
def recipe_detail(request: Request, id: int, db: Session = Depends(get_db)):
    recipe = _get_recipe_or_404(db, id)
    return templates.TemplateResponse(request, "recipe_detail.html", {"recipe": recipe})

@app.post("/recipe/new", response_class=RedirectResponse)
def create_recipe(
    db: Session = Depends(get_db),
    recipe_data: schemas.RecipeCreate = Depends(recipe_form),
    photo: Optional[UploadFile] = File(None)
):
    db_recipe = crud.create_recipe(db=db, recipe=recipe_data, photo_file=photo)
    return RedirectResponse(url=f"/recipe/{db_recipe.id}", status_code=303)

@app.get("/recipe/{id}/edit", response_class=HTMLResponse)
def edit_recipe_form(request: Request, id: int, db: Session = Depends(get_db)):
    recipe = _get_recipe_or_404(db, id)
    return templates.TemplateResponse(request, "recipe_form.html", {"recipe": recipe})

@app.post("/recipe/{id}/edit", response_class=RedirectResponse)
def edit_recipe(
    id: int,
    db: Session = Depends(get_db),
    recipe_data: schemas.RecipeCreate = Depends(recipe_form),
    photo: Optional[UploadFile] = File(None)
):
    db_recipe = crud.update_recipe(db=db, recipe_id=id, recipe=recipe_data, photo_file=photo)
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RedirectResponse(url=f"/recipe/{db_recipe.id}", status_code=303)

@app.post("/recipe/{id}/delete", response_class=RedirectResponse)
def delete_recipe(id: int, db: Session = Depends(get_db)):
    if crud.delete_recipe(db=db, recipe_id=id) is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RedirectResponse(url="/", status_code=303)

# API endpoints for Meal Planner
@app.get("/api/meal-plan", response_model=List[schemas.MealPlan])
def get_meal_plan_for_week(start_date: datetime.date, end_date: datetime.date, db: Session = Depends(get_db)):
    return crud.get_meal_plans(db, start_date=start_date, end_date=end_date)

@app.post("/api/meal-plan", response_model=schemas.MealPlan)
def add_meal_to_plan(meal_plan: schemas.MealPlanCreate, db: Session = Depends(get_db)):
    if meal_plan.recipe_id is not None and crud.get_recipe(db, recipe_id=meal_plan.recipe_id) is None:
        raise HTTPException(status_code=422, detail="Recipe not found")
    return crud.create_meal_plan(db=db, meal_plan=meal_plan)

@app.delete("/api/meal-plan/{meal_plan_id}")
def delete_meal_from_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    if crud.delete_meal_plan(db=db, meal_plan_id=meal_plan_id) is None:
        raise HTTPException(status_code=404, detail="Meal plan entry not found")
    return {"ok": True}

@app.get("/tag/{tag_name}", response_class=HTMLResponse)
def view_recipes_by_tag(request: Request, tag_name: str, db: Session = Depends(get_db)):
    recipes = crud.get_recipes_by_tag(db=db, tag_name=tag_name)
    return templates.TemplateResponse(request, "index.html", {"recipes": recipes, "tag_name": tag_name})
