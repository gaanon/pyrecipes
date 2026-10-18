"""backup_app.py and import_recipes.py: what a backup contains, and that it restores."""
import datetime
import json
import os
import stat
import tarfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import backup_app
import import_recipes
from app import crud, models, schemas
from tests.conftest import enforce_foreign_keys


def _sessionmaker(tmp_path, name):
    engine = create_engine(f"sqlite:///{tmp_path / name}")
    enforce_foreign_keys(engine)
    models.Base.metadata.create_all(engine)
    return sessionmaker(autoflush=False, bind=engine)


def _seed(session):
    soup = crud.create_recipe(session, schemas.RecipeCreate(
        name="Tomato Soup", servings="4", tags=["Soup", "Dinner"],
        ingredients=[
            schemas.IngredientCreate(name="Tomato", amount="6", order_index=0, group_name="Base"),
            schemas.IngredientCreate(name="Basil", amount="1 bunch", order_index=1, is_optional=True),
        ],
        instructions=[schemas.InstructionCreate(step_number=1, description="Simmer.")],
        notes=[schemas.NoteCreate(name="Tip", text="Better the next day.")],
    ))
    soup.photo_path = "uploads/soup.jpg"
    session.add_all([
        models.MealPlan(plan_date=datetime.date(2026, 10, 20), recipe_id=soup.id),
        models.MealPlan(plan_date=datetime.date(2026, 10, 21), custom_meal_name="Leftovers"),
    ])
    session.commit()
    return soup


def _snapshot(session):
    """Everything a restore must bring back, in a comparable shape."""
    recipes = []
    for r in session.query(models.Recipe).order_by(models.Recipe.id):
        recipes.append((
            r.id, r.name, r.servings, r.photo_path,
            sorted(rt.tag.name for rt in r.recipe_tags),
            [(i.name, i.amount, i.group_name, bool(i.is_optional), i.order_index) for i in r.ingredients],
            [(s.step_number, s.description) for s in r.instructions],
            [(n.name, n.text) for n in r.notes],
        ))
    meals = [(m.plan_date, m.recipe_id, m.custom_meal_name)
             for m in session.query(models.MealPlan).order_by(models.MealPlan.plan_date)]
    return recipes, meals


# --- JSON export / import ---------------------------------------------------------------

def test_json_backup_restores_into_an_empty_database(tmp_path):
    Source, Target = _sessionmaker(tmp_path, "source.db"), _sessionmaker(tmp_path, "target.db")
    with Source() as source:
        _seed(source)
        backup_app.export_recipes_to_json(source, tmp_path / "export.json")
        expected = _snapshot(source)

    with Target() as target:
        import_recipes.import_recipes(tmp_path / "export.json", target)
    with Target() as target:
        assert _snapshot(target) == expected
        assert expected[1], "the meal plan should be part of the backup"


def test_import_updates_existing_recipes_and_reuses_tags_ignoring_case(tmp_path):
    Session = _sessionmaker(tmp_path, "db.db")
    with Session() as session:
        soup = _seed(session)
        backup_app.export_recipes_to_json(session, tmp_path / "export.json")
    data = json.loads((tmp_path / "export.json").read_text())
    data["recipes"][0]["name"] = "Better Tomato Soup"
    data["recipes"][0]["tags"] = ["soup", "SOUP", "dinner"]  # existing tags, other spellings
    (tmp_path / "export.json").write_text(json.dumps(data))

    with Session() as session:
        import_recipes.import_recipes(tmp_path / "export.json", session)
    with Session() as session:
        saved = session.get(models.Recipe, soup.id)
        assert saved.name == "Better Tomato Soup"
        assert sorted(rt.tag.name for rt in saved.recipe_tags) == ["Dinner", "Soup"]
        assert session.query(models.Tag).count() == 2
        assert session.query(models.Recipe).count() == 1
        assert session.query(models.MealPlan).count() == 2  # not duplicated by a re-import


def test_failed_import_changes_nothing_and_exits_non_zero(tmp_path, capsys):
    Session = _sessionmaker(tmp_path, "db.db")
    backup = {"recipes": [
        {"id": 1, "name": "Fine", "ingredients": [], "instructions": [], "notes": [], "tags": []},
        {"id": 2, "name": "Broken", "ingredients": [{"name": "No amount"}]},
    ]}
    (tmp_path / "bad.json").write_text(json.dumps(backup))

    with pytest.raises(SystemExit) as exit_info:
        import_recipes.main([str(tmp_path / "bad.json")], session_factory=Session)

    assert exit_info.value.code != 0
    assert "Broken" in capsys.readouterr().err
    with Session() as session:
        assert session.query(models.Recipe).count() == 0


# --- mysqldump ------------------------------------------------------------------------------

FAKE_MYSQLDUMP = """#!/bin/sh
# Stand-in for mysqldump: records how it was called, then behaves like the real thing
if [ "$1" = "--version" ]; then echo "$FAKE_VERSION"; exit 0; fi
printf '%s\\n' "$@" > "$FAKE_LOG/args"
for a in "$@"; do case "$a" in --defaults-extra-file=*) cat "${a#*=}" > "$FAKE_LOG/defaults";; esac; done
if [ -n "$FAKE_FAIL" ]; then echo "-- partial output"; echo "Access denied for user" >&2; exit 2; fi
echo "CREATE TABLE \\`recipes\\` (id int);"
"""


@pytest.fixture
def fake_mysqldump(tmp_path, monkeypatch):
    bin_dir, log = tmp_path / "bin", tmp_path / "log"
    bin_dir.mkdir()
    log.mkdir()
    script = bin_dir / "mysqldump"
    script.write_text(FAKE_MYSQLDUMP)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_LOG", str(log))
    monkeypatch.setenv("FAKE_VERSION", "mysqldump from 11.8.3-MariaDB, client 10.19 for debian-linux-gnu (aarch64)")
    monkeypatch.setenv("DATABASE_URL", "mysql+pymysql://recipes:p%40ss%3Aw%2Frd@recipes-db:3307/recipe_db")
    return log


def test_mysqldump_gets_credentials_from_a_file_not_the_command_line(fake_mysqldump, tmp_path):
    backup_app.backup_database(tmp_path / "dump.sql")

    args = (fake_mysqldump / "args").read_text().splitlines()
    assert args[0].startswith("--defaults-extra-file=")  # mysqldump requires it first
    assert not any("p@ss:w/rd" in a or "--password" in a for a in args)
    defaults = (fake_mysqldump / "defaults").read_text()
    assert 'password="p@ss:w/rd"' in defaults
    assert "user=recipes" in defaults and "host=recipes-db" in defaults and "port=3307" in defaults
    assert args[-1] == "recipe_db"
    assert "--single-transaction" in args
    assert not os.path.exists(args[0].split("=", 1)[1]), "the credentials file is removed afterwards"


@pytest.mark.parametrize("version, tls_args", [
    ("mysqldump from 11.8.3-MariaDB, client 10.19", ["--ssl", "--skip-ssl-verify-server-cert"]),
    ("mysqldump  Ver 8.0.40 for Linux on x86_64 (MySQL Community Server - GPL)", ["--ssl-mode=REQUIRED"]),
])
def test_mysqldump_uses_tls_options_for_its_client_flavor(fake_mysqldump, tmp_path, monkeypatch, version, tls_args):
    monkeypatch.setenv("FAKE_VERSION", version)

    backup_app.backup_database(tmp_path / "dump.sql")

    args = (fake_mysqldump / "args").read_text().splitlines()
    assert all(a in args for a in tls_args)
    assert "--ssl=false" not in args


def test_failed_dump_leaves_no_partial_file_and_reports_why(fake_mysqldump, tmp_path, monkeypatch):
    monkeypatch.setenv("FAKE_FAIL", "1")

    with pytest.raises(backup_app.BackupError, match="Access denied"):
        backup_app.backup_database(tmp_path / "dump.sql")

    assert list(tmp_path.glob("dump.sql*")) == []


# --- the whole backup ---------------------------------------------------------------------

def test_backup_writes_json_sql_and_photos(fake_mysqldump, tmp_path, monkeypatch):
    monkeypatch.setenv("COPYFILE_DISABLE", "1")  # stop macOS tar adding ._ files (GNU tar in the image never does)
    Session = _sessionmaker(tmp_path, "db.db")
    with Session() as session:
        _seed(session)
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    (uploads / "soup.jpg").write_bytes(b"photo")
    backups = tmp_path / "backups"

    backup_dir = backup_app.main(0, "", backup_base_dir=backups, upload_dir=uploads, session_factory=Session)

    assert sorted(p.name for p in backup_dir.iterdir()) == ["database_backup.sql", "image_backup.tar.gz", "recipes_export.json"]
    assert "CREATE TABLE `recipes`" in (backup_dir / "database_backup.sql").read_text()
    with tarfile.open(backup_dir / "image_backup.tar.gz") as tar:
        assert [m for m in tar.getnames() if m.endswith(".jpg")] == ["./soup.jpg"]
    assert json.loads((backup_dir / "recipes_export.json").read_text())["recipes"][0]["name"] == "Tomato Soup"


def test_backup_fails_with_non_zero_exit_when_the_dump_fails(fake_mysqldump, tmp_path, monkeypatch):
    monkeypatch.setenv("FAKE_FAIL", "1")
    Session = _sessionmaker(tmp_path, "db.db")

    with pytest.raises(SystemExit) as exit_info:
        backup_app.main(0, "", backup_base_dir=tmp_path / "backups", upload_dir=tmp_path, session_factory=Session)

    assert exit_info.value.code != 0
