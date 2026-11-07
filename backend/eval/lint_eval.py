# Eval need the LLM running: python -m eval.lint_eval
import ast
import subprocess
import tempfile
import textwrap
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

CASES = [
    # js off-by-one: fix must be code only not explanation
    ("js-loop", "javascript", """
        function sum(x) {
          let s = 0;
          for (let i = 0; i <= x.length; i++) s += x[i];
          return s;
        }
    """, [3]),
    # arr[-1] is a bug in js
    ("js-neg-index", "javascript", """
        function last(arr) {
          if (arr.length === 0) return null;
          return arr[-1];
        }
    """, [3]),
    # arr[-1] is correct in python
    ("py-neg-index", "python", """
        def last(arr):
            if len(arr) == 0:
                return None
            return arr[-1]
    """, []),
    # correct code, it must not made up issues
    ("py-truthy", "python", """
        def is_empty(arr):
            return not arr
    """, []),
    # mutable default arg, also often breaks the json
    ("py-mutable", "python", """
        def add_item(item, bucket=[]):
            bucket.append(item)
            return bucket
    """, [1]),
    # 2 bugs in 1 function, must both be found
    ("py-multi", "python", """
        def stats(list):
            minimum = list[0]
            for x in list[1:]:
                if x > minimum:
                    minimum = x
            average = sum(list) / (len(list) - 1)
            return minimum, average
    """, [4, 6]),
]


def parses(lang, fix, opens_block):
    fix = textwrap.dedent(fix).rstrip()
    if opens_block and lang == "python" and fix.endswith(":"):
        fix += "\n    pass"
    if opens_block and lang == "javascript" and fix.endswith(")"):
        fix += " {}"
    if opens_block and lang == "javascript" and fix.endswith("{"):
        fix += "}"
    if lang == "python":
        for src in (fix, "def _():\n" + textwrap.indent(fix, "    ")):
            try:
                ast.parse(src)
                return True
            except SyntaxError:
                pass
        return False
    for src in (fix, "function _() {\n" + fix + "\n}"):
        with tempfile.NamedTemporaryFile("w", suffix=".js") as f:
            f.write(src)
            f.flush()
            if subprocess.run(["node", "--check", f.name], capture_output=True).returncode == 0:
                return True
    return False


def check(client, lang, code, bug_lines):
    r = client.post("/lint", json={"language": lang, "code": code})
    if r.status_code != 200:
        return [f"HTTP {r.status_code}: {r.json()}"]
    issues = r.json()["issues"]
    lines = code.splitlines()
    n = len(lines)
    problems = []
    if not bug_lines and issues:
        problems.append(f"{len(issues)} issue found on correct code")
    for line in bug_lines:
        if not any(i["line_start"] <= line <= i["line_end"] for i in issues):
            problems.append(f"missed bug on line {line}")
    for i in issues:
        if not 1 <= i["line_start"] <= i["line_end"] <= n:
            problems.append(f"lines {i['line_start']}-{i['line_end']} outside 1-{n}")
        replaced = lines[i["line_start"] - 1:i["line_end"]]
        opens_block = bool(replaced) and replaced[-1].rstrip().endswith((":", "{", ")"))
        if "\\n" in i["fix"] or "```" in i["fix"] or not parses(lang, i["fix"], opens_block):
            problems.append(f"fix is not just a code: {i['fix'][:70]!r}")
    return problems


def main():
    print(f"model: {settings.llm_model}, prompt: {settings.llm_prompt_version}, json mode: {settings.llm_json_mode}\n")
    passed = 0
    with TestClient(app) as client:
        for name, lang, code, bug_lines in CASES:
            problems = check(client, lang, textwrap.dedent(code).lstrip("\n"), bug_lines)
            passed += not problems
            print(f"{'PASS' if not problems else 'FAIL'} {name}", *problems, sep="\n  ")
    print(f"\n{passed}/{len(CASES)} passed")


if __name__ == "__main__":
    main()
