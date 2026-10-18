"""The planner's date helpers (app/static/js/dates.js), run in Node under different time zones."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

DATES_JS = Path(__file__).resolve().parent.parent / "app" / "static" / "js" / "dates.js"

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")


def _run(tz, expression):
    script = f"const d = require({json.dumps(str(DATES_JS))}); console.log(JSON.stringify({expression}));"
    result = subprocess.run(["node", "-e", script], env={**os.environ, "TZ": tz}, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


@pytest.mark.parametrize("tz, local_time, expected", [
    ("Europe/London", "2026, 6, 15, 0, 30", "2026-07-15"),     # just after midnight in summer time (UTC+1)
    ("America/New_York", "2026, 9, 20, 21, 0", "2026-10-20"),  # evening, already the next day in UTC
    ("UTC", "2026, 9, 20, 12, 0", "2026-10-20"),
])
def test_format_date_uses_the_local_calendar_day(tz, local_time, expected):
    assert _run(tz, f"d.formatDate(new Date({local_time}))") == expected


def test_week_runs_monday_to_sunday_in_local_time():
    # Sunday evening in New York (already Monday in UTC) belongs to the week of Monday 19 October
    week = _run(
        "America/New_York",
        "(() => { const w = d.getWeekRange(new Date(2026, 9, 25, 22, 0)); return [d.formatDate(w.start), d.formatDate(w.end)]; })()",
    )
    assert week == ["2026-10-19", "2026-10-25"]
