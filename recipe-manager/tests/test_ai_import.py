import json
from types import SimpleNamespace

from app import ai_service


class _FakeClient:
    """Stands in for the OpenAI-compatible API, which is external and costs money."""

    def __init__(self, content):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )))


def test_process_recipe_image_returns_parsed_recipe(client, monkeypatch):
    model_output = {
        "name": "Pancakes",
        "servings": "4",
        "ingredients": [
            {"name": "Flour", "amount": "200g", "order_index": 7},
            {"name": "Milk", "amount": "300ml", "order_index": 7},
        ],
        "instructions": [{"step_number": 9, "description": "Mix."}],
        "notes": [],
        "tags": ["breakfast"],
    }
    monkeypatch.setattr(ai_service, "_get_client", lambda: _FakeClient("```json\n" + json.dumps(model_output) + "\n```"))

    response = client.post("/api/process-recipe-image", files={"file": ("r.jpg", b"fake-image", "image/jpeg")})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Pancakes"
    assert body["tags"] == ["breakfast"]
    assert [(i["name"], i["order_index"]) for i in body["ingredients"]] == [("Flour", 0), ("Milk", 1)]
    assert [s["step_number"] for s in body["instructions"]] == [1]
