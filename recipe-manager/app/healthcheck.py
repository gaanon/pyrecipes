"""Container health check: exits 0 if the app's /healthz answers 200, 1 otherwise.

The Quadlet unit runs it as `python -m app.healthcheck`. It's a script rather than a
`python -c "..."` one-liner because Quadlet mangles quotes inside HealthCmd.
"""
import sys
import urllib.request

URL = "http://127.0.0.1:8000/healthz"


def main(url: str = URL) -> int:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return 0 if response.status == 200 else 1
    except Exception as e:  # HTTP 503, connection refused, timeout...
        print(f"unhealthy: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
