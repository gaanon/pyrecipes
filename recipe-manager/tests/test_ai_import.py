"""The AI recipe scan, against a fake OpenAI-compatible provider.

Only the HTTP transport is faked: the real OpenAI SDK builds the request and handles
the response, retries and timeouts, so these tests see what production sees.
"""
import asyncio
import base64
import io
import json

import httpx
import httpx2
import pytest
from PIL import Image

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


def _completion(content, finish_reason="stop", refusal=None):
    return {
        "id": "chatcmpl-test", "object": "chat.completion", "created": 0, "model": "test-model",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content, "refusal": refusal},
                     "finish_reason": finish_reason}],
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


def test_connection_failure_logs_the_underlying_reason(client, provider, caplog):
    # httpx errors often have an empty message, so the log must name the error type too
    provider.error = httpx2.ConnectError("")

    response = _scan(client)

    assert response.status_code == 502
    assert "ConnectError" in caplog.text


def test_answer_cut_off_by_the_token_limit_says_so(client, provider, caplog):
    # e.g. the model spent its whole token budget thinking and wrote no text
    provider.reply = _completion(None, finish_reason="length")

    response = _scan(client)

    assert response.status_code == 502
    assert "token limit" in response.json()["detail"]
    assert "finish_reason=length" in caplog.text
    assert "image=image/jpeg, 11 bytes" in caplog.text  # what was sent, to spot unsupported formats


def _image(size, fmt, orientation=None):
    exif = Image.Exif()
    if orientation:
        exif[0x0112] = orientation
    out = io.BytesIO()
    Image.new("RGB", size, "white").save(out, fmt, exif=exif)
    return out.getvalue()


def _sent_image(provider):
    [request] = provider.requests
    url = request["messages"][0]["content"][1]["image_url"]["url"]
    header, data = url.split(",", 1)
    return header, Image.open(io.BytesIO(base64.b64decode(data)))


def test_large_photo_is_shrunk_before_sending(client, provider):
    # A full-size phone photo becomes ~12k image tokens and can exhaust the GPU's memory
    photo = _image((4000, 3000), "JPEG")

    client.post("/api/process-recipe-image", files={"file": ("recipe.jpg", photo, "image/jpeg")})

    header, sent = _sent_image(provider)
    assert header == "data:image/jpeg;base64"
    assert max(sent.size) == ai_service.AI_IMAGE_MAX_SIDE
    assert sent.size == (1280, 960)


def test_shrunk_photo_is_turned_upright(client, provider):
    # Phones save portrait photos sideways plus an EXIF "rotate 90°" tag, which re-encoding drops
    photo = _image((4000, 3000), "JPEG", orientation=6)

    client.post("/api/process-recipe-image", files={"file": ("recipe.jpg", photo, "image/jpeg")})

    _, sent = _sent_image(provider)
    assert sent.size == (960, 1280)


def test_large_png_with_transparency_is_sent_as_jpeg(client, provider):
    out = io.BytesIO()
    Image.new("RGBA", (3000, 2000)).save(out, "PNG")

    client.post("/api/process-recipe-image", files={"file": ("recipe.png", out.getvalue(), "image/png")})

    header, sent = _sent_image(provider)
    assert header == "data:image/jpeg;base64"
    assert sent.size == (1280, 853)


def test_small_photo_is_sent_unchanged(client, provider):
    photo = _image((800, 600), "PNG")

    client.post("/api/process-recipe-image", files={"file": ("recipe.png", photo, "image/png")})

    [request] = provider.requests
    assert request["messages"][0]["content"][1]["image_url"]["url"] == \
        "data:image/png;base64," + base64.b64encode(photo).decode()


def test_refusal_is_reported(client, provider):
    provider.reply = _completion(None, refusal="I can't help with that.")

    response = _scan(client)

    assert response.status_code == 502
    assert "I can't help with that." in response.json()["detail"]
