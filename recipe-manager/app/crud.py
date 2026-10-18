import datetime
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, joinedload
from . import models, schemas

_WITH_TAGS = joinedload(models.Recipe.recipe_tags).joinedload(models.RecipeTag.tag)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
# Stored in Recipe.photo_path and served by the /uploads mount
PHOTO_PATH_PREFIX = "uploads/"

def save_photo(photo_file: UploadFile) -> str:
    """Saves the uploaded photo and returns its photo_path."""
    ext = Path(photo_file.filename).suffix
    filename = f"{uuid.uuid4()}{ext}"
    with (UPLOAD_DIR / filename).open("wb") as buffer:
        shutil.copyfileobj(photo_file.file, buffer)
    return PHOTO_PATH_PREFIX + filename

def delete_photo(photo_path: Optional[str]):
    """Removes a photo saved by save_photo; anything else (no photo, the placeholder) is left alone."""
    if photo_path and photo_path.startswith(PHOTO_PATH_PREFIX):
        (UPLOAD_DIR / Path(photo_path).name).unlink(missing_ok=True)

def get_recipes(db: Session, skip: int = 0, limit: int = 100):
    return db.scalars(select(models.Recipe).options(_WITH_TAGS).offset(skip).limit(limit)).unique().all()

def search_recipes(db: Session, query: str):
    return db.scalars(select(models.Recipe).options(_WITH_TAGS).where(models.Recipe.name.contains(query))).unique().all()

def get_recipes_by_tag(db: Session, tag_name: str):
    return db.scalars(
        select(models.Recipe).join(models.Recipe.recipe_tags).join(models.RecipeTag.tag).where(models.Tag.name == tag_name)
    ).all()

def get_recipe(db: Session, recipe_id: int):
    return db.get(models.Recipe, recipe_id, options=[_WITH_TAGS])

def get_tag_by_name(db: Session, name: str):
    # Case-insensitive, matching MySQL's default collation (and the unique index on tags.name)
    return db.scalar(select(models.Tag).where(func.lower(models.Tag.name) == name.lower()))

def create_tag(db: Session, tag: schemas.TagCreate):
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.flush()  # committed with the rest of the save; flushed so later lookups find it
    return db_tag

def _link_tags(db: Session, db_recipe: models.Recipe, tag_names: list[str]):
    """Link tags to the recipe, once each: "Soup, soup" is one tag. Existing tags keep their spelling."""
    # Deduplicated by tag id, so whatever the database collation treats as equal is linked once
    linked_tag_ids = set()
    for tag_name in (name.strip() for name in tag_names):
        if not tag_name:
            continue
        db_tag = get_tag_by_name(db, name=tag_name)
        if not db_tag:
            db_tag = create_tag(db, schemas.TagCreate(name=tag_name))
        if db_tag.id not in linked_tag_ids:
            linked_tag_ids.add(db_tag.id)
            db_recipe.recipe_tags.append(models.RecipeTag(tag=db_tag))

def _apply_recipe(db: Session, db_recipe: models.Recipe, recipe: schemas.RecipeCreate):
    """Sets the recipe's fields and replaces its ingredients, instructions, notes and tags."""
    db_recipe.name = recipe.name
    db_recipe.servings = recipe.servings
    db_recipe.ingredients = [models.Ingredient(**i.model_dump()) for i in recipe.ingredients]
    db_recipe.instructions = [models.Instruction(**i.model_dump()) for i in recipe.instructions]
    db_recipe.notes = [models.Note(**n.model_dump()) for n in recipe.notes]
    db_recipe.recipe_tags = []
    _link_tags(db, db_recipe, recipe.tags)

def _save_recipe(db: Session, db_recipe: models.Recipe, recipe: schemas.RecipeCreate, photo_file: Optional[UploadFile]):
    """Saves everything in one transaction. On failure nothing is kept, including a newly uploaded photo;
    a replaced photo file is only deleted once the new one is committed."""
    new_photo = save_photo(photo_file) if photo_file and photo_file.filename else None
    old_photo = db_recipe.photo_path
    try:
        db.add(db_recipe)
        _apply_recipe(db, db_recipe, recipe)
        if new_photo:
            db_recipe.photo_path = new_photo
        db.commit()
    except Exception:
        db.rollback()
        delete_photo(new_photo)
        raise
    if new_photo:
        delete_photo(old_photo)
    db.refresh(db_recipe)
    return db_recipe

def create_recipe(db: Session, recipe: schemas.RecipeCreate, photo_file: Optional[UploadFile] = None):
    return _save_recipe(db, models.Recipe(), recipe, photo_file)

def update_recipe(db: Session, recipe_id: int, recipe: schemas.RecipeCreate, photo_file: Optional[UploadFile] = None):
    """Returns None if the recipe doesn't exist."""
    db_recipe = get_recipe(db, recipe_id)
    if not db_recipe:
        return None
    return _save_recipe(db, db_recipe, recipe, photo_file)

def delete_recipe(db: Session, recipe_id: int):
    db_recipe = get_recipe(db, recipe_id)
    if db_recipe:
        # Keep planned meals for this recipe, as custom meals carrying its name
        db.execute(
            update(models.MealPlan)
            .where(models.MealPlan.recipe_id == recipe_id)
            .values(recipe_id=None, custom_meal_name=func.coalesce(models.MealPlan.custom_meal_name, db_recipe.name))
        )
        db.delete(db_recipe)
        db.commit()
        delete_photo(db_recipe.photo_path)
    return db_recipe

def get_meal_plans(db: Session, start_date: datetime.date, end_date: datetime.date):
    return db.scalars(select(models.MealPlan).where(models.MealPlan.plan_date.between(start_date, end_date))).all()

def create_meal_plan(db: Session, meal_plan: schemas.MealPlanCreate):
    db_meal_plan = models.MealPlan(**meal_plan.model_dump())
    db.add(db_meal_plan)
    db.commit()
    db.refresh(db_meal_plan)
    return db_meal_plan

def delete_meal_plan(db: Session, meal_plan_id: int):
    db_meal_plan = db.get(models.MealPlan, meal_plan_id)
    if db_meal_plan:
        db.delete(db_meal_plan)
        db.commit()
    return db_meal_plan