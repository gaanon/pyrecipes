"""Saving a recipe is all-or-nothing, and photo files on disk follow the database."""
import json

import pytest

from app import crud, models


def _form(name="Tomato Soup", ingredient="Tomato", tags="soup"):
    return {
        "name": name,
        "servings": "4",
        "tags": tags,
        "ingredients": json.dumps([{"name": ingredient, "amount": "1", "order_index": 0}]),
        "instructions": json.dumps([{"step_number": 1, "description": "Cook."}]),
        "notes": json.dumps([]),
    }


def _photo(content=b"jpeg-bytes"):
    return {"photo": ("dish.jpg", content, "image/jpeg")}


def _create_via_form(client):
    response = client.post("/recipe/new", data=_form(), files=_photo(b"original"), follow_redirects=False)
    assert response.status_code == 303
    return int(response.headers["location"].rsplit("/", 1)[1])


def _files(upload_dir):
    return sorted(p.read_bytes() for p in upload_dir.iterdir())


def _fail_on_commit(monkeypatch, db_session):
    """Simulates the database rejecting the commit after the rows were already sent (flushed)."""
    def commit():
        db_session.flush()
        raise RuntimeError("database went away")
    monkeypatch.setattr(db_session, "commit", commit)


def test_failed_create_saves_nothing(client_500, db_session, upload_dir, monkeypatch):
    _fail_on_commit(monkeypatch, db_session)

    response = client_500.post("/recipe/new", data=_form(), files=_photo(), follow_redirects=False)

    assert response.status_code == 500
    db_session.expire_all()
    assert db_session.query(models.Recipe).count() == 0
    assert db_session.query(models.Ingredient).count() == 0
    assert _files(upload_dir) == []


def test_failed_update_leaves_recipe_and_photo_unchanged(client, client_500, db_session, upload_dir, monkeypatch):
    recipe_id = _create_via_form(client)
    original_photo = crud.get_recipe(db_session, recipe_id).photo_path
    _fail_on_commit(monkeypatch, db_session)

    response = client_500.post(
        f"/recipe/{recipe_id}/edit", data=_form(name="Renamed", ingredient="Basil"), files=_photo(b"new"),
        follow_redirects=False,
    )

    assert response.status_code == 500
    db_session.expire_all()
    saved = crud.get_recipe(db_session, recipe_id)
    assert saved.name == "Tomato Soup"
    assert [i.name for i in saved.ingredients] == ["Tomato"]
    assert saved.photo_path == original_photo
    assert _files(upload_dir) == [b"original"]


def test_replacing_a_photo_deletes_the_old_file(client, db_session, upload_dir):
    recipe_id = _create_via_form(client)

    client.post(f"/recipe/{recipe_id}/edit", data=_form(), files=_photo(b"replacement"), follow_redirects=False)

    assert _files(upload_dir) == [b"replacement"]
    db_session.expire_all()
    photo_path = crud.get_recipe(db_session, recipe_id).photo_path
    assert client.get("/" + photo_path).content == b"replacement"


def test_editing_without_choosing_a_photo_keeps_the_current_one(client, db_session, upload_dir):
    recipe_id = _create_via_form(client)
    original_photo = crud.get_recipe(db_session, recipe_id).photo_path

    # Browsers send an empty file part when the photo input is left blank
    empty_file = {"photo": ("", b"", "application/octet-stream")}
    response = client.post(f"/recipe/{recipe_id}/edit", data=_form(), files=empty_file, follow_redirects=False)

    assert response.status_code == 303
    db_session.expire_all()
    assert crud.get_recipe(db_session, recipe_id).photo_path == original_photo
    assert _files(upload_dir) == [b"original"]


def test_deleting_a_recipe_deletes_its_photo(client, upload_dir):
    recipe_id = _create_via_form(client)

    client.post(f"/recipe/{recipe_id}/delete", follow_redirects=False)

    assert _files(upload_dir) == []
