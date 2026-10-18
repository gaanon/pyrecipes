from pydantic import BaseModel, ConfigDict, model_validator
from typing import List, Optional
import datetime

class IngredientBase(BaseModel):
    group_name: Optional[str] = None
    name: str
    amount: str
    is_optional: bool = False
    order_index: int

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    recipe_id: int

    model_config = ConfigDict(from_attributes=True)

class InstructionBase(BaseModel):
    step_number: int
    description: str

class InstructionCreate(InstructionBase):
    pass

class Instruction(InstructionBase):
    id: int
    recipe_id: int

    model_config = ConfigDict(from_attributes=True)

class NoteBase(BaseModel):
    name: str
    text: str

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    recipe_id: int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# Define Recipe schemas BEFORE MealPlan schemas that depend on it
class RecipeBase(BaseModel):
    name: str
    servings: Optional[str] = None

class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate] = []
    instructions: List[InstructionCreate] = []
    notes: List[NoteCreate] = []
    tags: List[str] = [] # We'll handle tag creation logic in the endpoint

class Recipe(RecipeBase):
    id: int
    photo_path: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    ingredients: List[Ingredient] = []
    instructions: List[Instruction] = []
    notes: List[Note] = []
    tags: List[Tag] = []

    model_config = ConfigDict(from_attributes=True)

# Now define MealPlan schemas
class MealPlanBase(BaseModel):
    plan_date: datetime.date
    recipe_id: Optional[int] = None
    custom_meal_name: Optional[str] = None

class MealPlanCreate(MealPlanBase):
    @model_validator(mode="after")
    def _recipe_or_custom_meal(self):
        if self.recipe_id is None and not (self.custom_meal_name or "").strip():
            raise ValueError("a meal needs either a recipe_id or a custom_meal_name")
        return self

class MealPlan(MealPlanBase):
    id: int
    recipe: Optional[Recipe] = None

    model_config = ConfigDict(from_attributes=True)
