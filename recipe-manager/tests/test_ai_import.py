"""The AI recipe scan, against a fake OpenAI-compatible provider.

Only the HTTP transport is faked: the real OpenAI SDK builds the request and handles
the response, retries and timeouts, so these tests see what production sees.
"""
import asyncio
import base64
import json

import httpx
import httpx2
import pytest

from app import ai_service
from app.main import app

PANCAKES = {
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


def _completion(content):
    return {
        "id": "chatcmpl-test", "object": "chat.completion", "created": 0, "model": "test-model",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
    }


class FakeProvider:
    def __init__(self):
        self.reply = _completion(json.dumps(PANCAKES))
        self.status = 200
        self.delay = 0
        self.error = None
        self.requests = []

    async def handle(self, request):
        self.requests.append(json.loads(request.content))
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error:
            raise self.error
        return httpx2.Response(self.status, json=self.reply if self.status == 200 else {"error": {"message": "nope"}})


@pytest.fixture
def provider(monkeypatch):
    fake = FakeProvider()
    monkeypatch.setenv("AI_API_KEY", "test-key")
    monkeypatch.setenv("AI_API_BASE_URL", "http://ai.test/v1")
    monkeypatch.setenv("AI_MODEL", "test-model")
    real_get_client = ai_service._get_client
    monkeypatch.setattr(
        ai_service, "_get_client",
        # No retries, so error cases don't wait for the SDK's backoff
        lambda: real_get_client(http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(fake.handle))).with_options(max_retries=0),
    )
    return fake


def _scan(client, content_type="image/jpeg"):
    return client.post("/api/process-recipe-image", files={"file": ("recipe", b"image-bytes", content_type)})


def test_scan_returns_the_parsed_recipe(client, provider):
    response = _scan(client)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Pancakes"
    assert body["tags"] == ["breakfast"]
    assert [(i["name"], i["order_index"]) for i in body["ingredients"]] == [("Flour", 0), ("Milk", 1)]
    assert [s["step_number"] for s in body["instructions"]] == [1]


def test_scan_sends_the_image_with_its_real_type(client, provider):
    _scan(client, content_type="image/png")

    [request] = provider.requests
    assert request["model"] == "test-model"
    image_url = request["messages"][0]["content"][1]["image_url"]["url"]
    assert image_url == "data:image/png;base64," + base64.b64encode(b"image-bytes").decode()


@pytest.mark.parametrize("content", [
    "```json\n" + json.dumps(PANCAKES) + "\n```",
    "```json\n" + json.dumps(PANCAKES) + "```",  # no newline before the closing fence
    "```\n" + json.dumps(PANCAKES) + "\n```",    # fence without a language
    "Here is the recipe:\n" + json.dumps(PANCAKES),
])
def test_scan_accepts_json_wrapped_in_markdown_or_text(client, provider, content):
    provider.reply = _completion(content)

    response = _scan(client)

    assert response.status_code == 200
    assert response.json()["name"] == "Pancakes"


@pytest.mark.parametrize("content", [
    "Sorry, I can't read this image.",                        # no JSON at all
    json.dumps({"name": "Pancakes", "ingredients": "flour"}),  # JSON, but not a valid recipe
    None,                                                      # empty message
])
def test_unusable_ai_answer_is_a_502_not_a_fake_recipe(client, provider, content):
    provider.reply = _completion(content)

    response = _scan(client)

    assert response.status_code == 502
    assert "name" not in response.json()


def test_provider_error_is_a_502_naming_the_status(client, provider):
    provider.status = 403

    response = _scan(client)

    assert response.status_code == 502
    assert "403" in response.json()["detail"]


def test_provider_timeout_is_a_504(client, provider):
    provider.error = httpx2.ReadTimeout("took too long")

    response = _scan(client)

    assert response.status_code == 504


def test_scan_does_not_block_other_requests(provider):
    provider.delay = 0.5
    finished = []

    async def scenario():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://app") as c:
            async def scan():
                await c.post("/api/process-recipe-image", files={"file": ("r.jpg", b"img", "image/jpeg")})
                finished.append("scan")

            async def open_page():
                await asyncio.sleep(0.1)
                await c.get("/recipe/new")
                finished.append("page")

            await asyncio.gather(scan(), open_page())

    asyncio.run(scenario())

    assert finished == ["page", "scan"]
