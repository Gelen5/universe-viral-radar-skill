import json
from pathlib import Path

from universe_viral_radar.profile import validate_profile


def test_profile_validation(tmp_path: Path):
    path = tmp_path / "profile.json"
    path.write_text(json.dumps({}), encoding="utf-8")
    ok, errors, _ = validate_profile(path)
    assert not ok
    assert errors
