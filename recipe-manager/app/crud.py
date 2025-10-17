import datetime
from sqlalchemy.orm import Session
from . import models, schemas

from sqlalchemy.orm import joinedload

def get_recipes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Recipe).options(joinedload(models.Recipe.recipe_tags).joinedload(models.RecipeTag.tag)).offset(skip).limit(limit).all()

def search_recipes(db: Session, query: str):
    return db.query(models.Recipe).options(joinedload(models.Recipe.recipe_tags).joinedload(models.RecipeTag.tag)).filter(models.Recipe.name.contains(query)).all()

def get_recipes_by_tag(db: Session, tag_name: str):
    return db.query(models.Recipe).join(models.RecipeTag).join(models.Tag).filter(models.Tag.name == tag_name).all()

def get_recipe(db: Session, recipe_id: int):
    return db.query(models.Recipe).options(joinedload(models.Recipe.recipe_tags).joinedload(models.RecipeTag.tag)).filter(models.Recipe.id == recipe_id).first()

def get_tag_by_name(db: Session, name: str):
    return db.query(models.Tag).filter(models.Tag.name == name).first()

def create_tag(db: Session, tag: schemas.TagCreate):
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def create_recipe(db: Session, recipe: schemas.RecipeCreate):
    # Create the main recipe object
    db_recipe = models.Recipe(name=recipe.name, servings=recipe.servings)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    # Handle Ingredients
    for ingredient_data in recipe.ingredients:
        db_ingredient = models.Ingredient(**ingredient_data.dict(), recipe_id=db_recipe.id)
        db.add(db_ingredient)

    # Handle Instructions
    for instruction_data in recipe.instructions:
        db_instruction = models.Instruction(**instruction_data.dict(), recipe_id=db_recipe.id)
        db.add(db_instruction)

    # Handle Notes
    for note_data in recipe.notes:
        db_note = models.Note(**note_data.dict(), recipe_id=db_recipe.id)
        db.add(db_note)

    # Handle Tags
    for tag_name in recipe.tags:
        db_tag = get_tag_by_name(db, name=tag_name)
        if not db_tag:
            db_tag = create_tag(db, schemas.TagCreate(name=tag_name))
        
        recipe_tag_link = models.RecipeTag(recipe_id=db_recipe.id, tag_id=db_tag.id)
        db.add(recipe_tag_link)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def update_recipe(db: Session, recipe_id: int, recipe: schemas.RecipeCreate):
    db_recipe = get_recipe(db, recipe_id)
    if not db_recipe:
        return None

    # Update main recipe fields
    db_recipe.name = recipe.name
    db_recipe.servings = recipe.servings

    # Clear existing relationships
    db_recipe.ingredients = []
    db_recipe.instructions = []
    db_recipe.notes = []
    db_recipe.recipe_tags = []

    # Handle Ingredients
    for ingredient_data in recipe.ingredients:
        db_ingredient = models.Ingredient(**ingredient_data.dict(), recipe_id=db_recipe.id)
        db.add(db_ingredient)

    # Handle Instructions
    for instruction_data in recipe.instructions:
        db_instruction = models.Instruction(**instruction_data.dict(), recipe_id=db_recipe.id)
        db.add(db_instruction)

    # Handle Notes
    for note_data in recipe.notes:
        db_note = models.Note(**note_data.dict(), recipe_id=db_recipe.id)
        db.add(db_note)

    # Handle Tags
    for tag_name in recipe.tags:
        db_tag = get_tag_by_name(db, name=tag_name)
        if not db_tag:
            db_tag = create_tag(db, schemas.TagCreate(name=tag_name))
        
        recipe_tag_link = models.RecipeTag(recipe_id=db_recipe.id, tag_id=db_tag.id)
        db.add(recipe_tag_link)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def delete_recipe(db: Session, recipe_id: int):
    db_recipe = get_recipe(db, recipe_id)
    if db_recipe:
        db.delete(db_recipe)
        db.commit()
    return db_recipe

def get_meal_plans(db: Session, start_date: datetime.date, end_date: datetime.date):
    return db.query(models.MealPlan).filter(models.MealPlan.plan_date.between(start_date, end_date)).all()

def create_meal_plan(db: Session, meal_plan: schemas.MealPlanCreate):
    db_meal_plan = models.MealPlan(**meal_plan.dict())
    db.add(db_meal_plan)
    db.commit()
    db.refresh(db_meal_plan)
    return db_meal_plan

def delete_meal_plan(db: Session, meal_plan_id: int):
    db_meal_plan = db.query(models.MealPlan).filter(models.MealPlan.id == meal_plan_id).first()
    if db_meal_plan:
        db.delete(db_meal_plan)
        db.commit()
    return db_meal_plan