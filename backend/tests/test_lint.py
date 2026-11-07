# Run: python -m pytest tests -q
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app, get_gateway

VALID = json.dumps({"issues": [
    {"line_start": 2, "line_end": 2, "severity": "high", "explanation": "b", "fix": "y = 2"},
    {"line_start": 1, "line_end": 1, "severity": "low", "explanation": "a", "fix": "x = 1"},
]})
CODE = {"language": "python", 
        "code": """
            x = 1
            y = 2
        """}

class FakeGateway:
    model = "fake"

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0

    async def complete(self, messages):
        self.calls += 1
        return self.replies.pop(0)

    async def close(self):
        pass

@pytest.fixture
def lint():
    def post(payload, replies):
        gateway = FakeGateway(replies)
        app.dependency_overrides[get_gateway] = lambda: gateway
        return TestClient(app).post("/lint", json=payload), gateway
    yield post
    app.dependency_overrides.clear()


# Bad input=422 before reaching LLM
@pytest.mark.parametrize("payload", [
    {"language": "python", "code": ""},
    {"language": "python", "code": " \n\t"},
    {"language": "typescript", "code": "let x = 1;"},
    {"language": "python", "code": "x" * 20001},
])
def test_rejects_bad_input(lint, payload):
    r, gateway = lint(payload, [])
    assert r.status_code == 422
    assert gateway.calls == 0


# not json is retried, and answer comes back as sorted by line
def test_retry_then_sorted_issues(lint):
    r, gateway = lint(CODE, ["not json", VALID])
    assert r.status_code == 200
    assert gateway.calls == 2
    assert [i["line_start"] for i in r.json()["issues"]] == [1, 2]


# line ranges outside the code are clamped to the real lines
def test_clamps_line_range(lint):
    issue = {"severity": "low", "explanation": "a", "fix": "x = 1"}
    reply = json.dumps({"issues": [
        {**issue, "line_start": 1, "line_end": 3},
        {**issue, "line_start": 9, "line_end": 4},
    ]})
    r, _ = lint({"language": "python", "code": "x = 1\ny = 2\n"}, [reply])
    assert [(i["line_start"], i["line_end"]) for i in r.json()["issues"]] == [(1, 2), (2, 2)]
