import json
from agent.run import write_json


def test_write_json_creates_parseable_artifact(tmp_path):
    path = tmp_path / "artifact.json"
    write_json(path, {"source": "https://example.com"})
    assert json.loads(path.read_text(encoding="utf-8"))["source"] == "https://example.com"
