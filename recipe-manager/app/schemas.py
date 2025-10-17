from pydantic import BaseModel
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

    class Config:
        orm_mode = True

class InstructionBase(BaseModel):
    step_number: int
    description: str

class InstructionCreate(InstructionBase):
    pass

class Instruction(InstructionBase):
    id: int
    recipe_id: int

    class Config:
        orm_mode = True

class NoteBase(BaseModel):
    name: str
    text: str

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    recipe_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True

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
    tags: List["Tag"] = [] # Use forward reference for robustness

    class Config:
        orm_mode = True

# Now define MealPlan schemas
class MealPlanBase(BaseModel):
    plan_date: datetime.date
    recipe_id: Optional[int] = None
    custom_meal_name: Optional[str] = None

class MealPlanCreate(MealPlanBase):
    pass

class MealPlan(MealPlanBase):
    id: int
    recipe: Optional["Recipe"] = None

    class Config:
        orm_mode = True

# Update forward references at the end of the file
Recipe.update_forward_refs()
MealPlan.update_forward_refs()