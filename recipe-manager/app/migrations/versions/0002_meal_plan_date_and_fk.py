"""meal_plans: plan_date as DATE, recipe FK ON DELETE SET NULL

Revision ID: 0002_meal_plan_date_and_fk
Revises: 0001_baseline
Create Date: 2026-10-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002_meal_plan_date_and_fk'
down_revision: Union[str, Sequence[str], None] = '0001_baseline'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK_NAME = "fk_meal_plans_recipe_id_recipes"
# Gives SQLite's unnamed foreign key a name so batch mode can drop it
NAMING_CONVENTION = {"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"}


def _existing_fk_name() -> str:
    # MySQL auto-named the baseline FK (e.g. meal_plans_ibfk_1); SQLite reports None
    if op.get_context().as_sql:
        return "meal_plans_ibfk_1"  # offline --sql preview: can't inspect, assume MySQL's default name
    for fk in sa.inspect(op.get_bind()).get_foreign_keys("meal_plans"):
        if fk["referred_table"] == "recipes":
            return fk["name"] or FK_NAME
    raise RuntimeError("meal_plans has no foreign key to recipes")


def _replace_fk(ondelete) -> None:
    fk_name = _existing_fk_name()
    with op.batch_alter_table("meal_plans", naming_convention=NAMING_CONVENTION) as batch_op:
        batch_op.drop_constraint(fk_name, type_="foreignkey")
        batch_op.create_foreign_key(FK_NAME, "recipes", ["recipe_id"], ["id"], ondelete=ondelete)


def _change_plan_date_type(new_type, old_type, convert_sql: str) -> None:
    if op.get_bind().dialect.name != "sqlite":
        # MySQL converts the stored values itself (DATETIME -> DATE truncates the time)
        op.alter_column("meal_plans", "plan_date", existing_type=old_type, type_=new_type, existing_nullable=False)
        return
    # SQLite batch mode would CAST the old text to the new type, which corrupts dates,
    # so copy the values into a new column explicitly and swap it in
    with op.batch_alter_table("meal_plans") as batch_op:
        batch_op.add_column(sa.Column("plan_date_new", new_type, nullable=True))
    op.execute(f"UPDATE meal_plans SET plan_date_new = {convert_sql}")
    with op.batch_alter_table("meal_plans") as batch_op:
        batch_op.drop_column("plan_date")
        batch_op.alter_column("plan_date_new", new_column_name="plan_date", existing_type=new_type, nullable=False)


def upgrade() -> None:
    _replace_fk("SET NULL")
    _change_plan_date_type(sa.Date(), sa.DateTime(), "date(plan_date)")


def downgrade() -> None:
    _change_plan_date_type(sa.DateTime(), sa.Date(), "datetime(plan_date)")
    _replace_fk(None)
