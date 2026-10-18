import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    photo_path: Mapped[Optional[str]] = mapped_column(String(500))
    servings: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    ingredients: Mapped[List["Ingredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", order_by="Ingredient.order_index"
    )
    instructions: Mapped[List["Instruction"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan", order_by="Instruction.step_number"
    )
    notes: Mapped[List["Note"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    recipe_tags: Mapped[List["RecipeTag"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recipe_id: Mapped[Optional[int]] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    group_name: Mapped[Optional[str]] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[str] = mapped_column(String(100))
    is_optional: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer)

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")


class Instruction(Base):
    __tablename__ = "instructions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recipe_id: Mapped[Optional[int]] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    step_number: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)

    recipe: Mapped["Recipe"] = relationship(back_populates="instructions")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recipe_id: Mapped[Optional[int]] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, default=func.now())

    recipe: Mapped["Recipe"] = relationship(back_populates="notes")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    recipe_tags: Mapped[List["RecipeTag"]] = relationship(back_populates="tag", cascade="all, delete-orphan")


class RecipeTag(Base):
    __tablename__ = "recipe_tags"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="recipe_tags")
    tag: Mapped["Tag"] = relationship(back_populates="recipe_tags")


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plan_date: Mapped[datetime.date] = mapped_column(Date)
    recipe_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recipes.id", ondelete="SET NULL", name="fk_meal_plans_recipe_id_recipes")
    )
    custom_meal_name: Mapped[Optional[str]] = mapped_column(String(255))

    recipe: Mapped[Optional["Recipe"]] = relationship()
