"""app/healthcheck.py: the container's HealthCmd. Exit 0 only when /healthz answers 200."""
import http.server
import threading

import pytest

from app import healthcheck


@pytest.fixture
def server():
    class Handler(http.server.BaseHTTPRequestHandler):
        status = 200

        def do_GET(self):
            self.send_response(Handler.status)
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, *args):
            pass

    httpd = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield Handler, f"http://127.0.0.1:{httpd.server_port}/healthz"
    httpd.shutdown()


def test_healthy_when_healthz_answers_200(server):
    _, url = server
    assert healthcheck.main(url) == 0


def test_unhealthy_when_healthz_answers_503(server, capsys):
    handler, url = server
    handler.status = 503
    assert healthcheck.main(url) == 1
    assert "503" in capsys.readouterr().err


def test_unhealthy_when_nothing_is_listening():
    assert healthcheck.main("http://127.0.0.1:9/healthz") == 1
