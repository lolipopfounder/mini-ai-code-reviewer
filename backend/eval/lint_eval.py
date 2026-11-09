# Eval need the LLM running: python -m eval.lint_eval
import ast
import subprocess
import tempfile
import textwrap
import time
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
    # long python file, 3 bugs
    ("py-long", "python", """
        from datetime import date


        class Inventory:
            def __init__(self):
                self.stock = {}

            def add(self, sku, qty):
                if qty <= 0:
                    raise ValueError("qty must be positive")
                self.stock[sku] = self.stock.get(sku, 0) + qty

            def remove(self, sku, qty):
                have = self.stock.get(sku, 0)
                if qty > have:
                    raise ValueError("not enough stock")
                self.stock[sku] = have - qty


        def order_total(items, discount_percent=0):
            total = 0
            for item in items:
                total += item["price"] * item["qty"]
            return total - total * discount_percent


        def paginate(rows, page, page_size):
            # page starts at 1
            start = page * page_size
            end = start + page_size
            return rows[start:end]


        def is_expired(expiry, today=None):
            today = today or date.today()
            return expiry > today


        def average_rating(reviews):
            if not reviews:
                return 0
            return sum(r["stars"] for r in reviews) / len(reviews)
    """, [24, 29, 36]),
    # long js file, 4 bugs
    ("js-long", "javascript", """
        function groupBy(items, key) {
          const out = {};
          for (const item of items) {
            const k = item[key];
            if (!out[k]) out[k] = [];
            out[k].push(item);
          }
          return out;
        }

        function maxPrice(products) {
          return products.reduce((max, p) => (p.price > max ? p.price : max));
        }

        async function loadUsers(ids, fetchUser) {
          const users = [];
          ids.forEach(async (id) => {
            users.push(await fetchUser(id));
          });
          return users;
        }

        function isWeekend(date) {
          const day = date.getDay();
          return day === 6 || day === 7;
        }

        function removeItem(list, value) {
          const i = list.indexOf(value);
          if (i) list.splice(i, 1);
          return list;
        }
    """, [12, 17, 25, 30]),
    # transfer deposits before checking withdraw
    ("py-class-state", "python", """
        class Account:
            def __init__(self, balance=0):
                self.balance = balance

            def deposit(self, amount):
                self.balance += amount

            def withdraw(self, amount):
                if amount > self.balance:
                    return False
                self.balance -= amount
                return True

            def transfer(self, other, amount):
                other.deposit(amount)
                return self.withdraw(amount)
    """, [15]),
    # long correct js
    ("js-long-clean", "javascript", """
        function chunk(arr, size) {
          const out = [];
          for (let i = 0; i < arr.length; i += size) {
            out.push(arr.slice(i, i + size));
          }
          return out;
        }

        function unique(arr) {
          return [...new Set(arr)];
        }

        function debounce(fn, ms) {
          let timer;
          return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn(...args), ms);
          };
        }

        function clamp(x, lo, hi) {
          return Math.min(Math.max(x, lo), hi);
        }
    """, []),
]


def is_python(code):
    for src in [code, "def f():\n" + textwrap.indent(code, "    ")]:
        try:
            ast.parse(src)
            return True
        except SyntaxError:
            pass
    return False


def is_js(code):
    for src in [code, "function f() {\n" + code + "\n}"]:
        with tempfile.NamedTemporaryFile("w", suffix=".js") as f:
            f.write(src)
            f.flush()
            result = subprocess.run(["node", "--check", f.name], capture_output=True)
            if result.returncode == 0:
                return True
    return False

# to check if a fix is just code
def is_code(lang, fix, old_line):
    fix = textwrap.dedent(fix).rstrip()
    if "\\n" in fix or "```" in fix:
        return False

    old_line = old_line.rstrip()
    if lang == "python":
        if fix.endswith(":") and old_line.endswith(":"):
            fix += "\n    pass"
        return is_python(fix)

    if fix.endswith(")") and old_line.endswith(")"):
        fix += " {}"
    if fix.endswith("{") and old_line.endswith("{"):
        fix += "}"
    return is_js(fix)


def check(client, lang, code, bug_lines):
    start = time.time()
    r = client.post("/lint", json={"language": lang, "code": code})
    seconds = time.time() - start
    if r.status_code != 200:
        return [f"HTTP {r.status_code}: {r.json()}"], seconds

    issues = r.json()["issues"]
    lines = code.splitlines()
    problems = []

    if not bug_lines and issues:
        problems.append(f"{len(issues)} issue found on correct code")

    for line in bug_lines:
        found = False
        for issue in issues:
            if issue["line_start"] <= line <= issue["line_end"]:
                found = True
        if not found:
            problems.append(f"missed bug on line {line}")

    for issue in issues:
        start, end = issue["line_start"], issue["line_end"]
        if start < 1 or end > len(lines) or start > end:
            problems.append(f"lines {start}-{end} outside 1-{len(lines)}")
            continue
        if not is_code(lang, issue["fix"], lines[end - 1]):
            problems.append(f"fix is not just a code: {issue['fix'][:70]!r}")

    return problems, seconds


def main():
    print(f"model: {settings.llm_model}, prompt: {settings.llm_prompt_version}, json mode: {settings.llm_json_mode}")
    print()
    passed = 0
    times = []
    with TestClient(app) as client:
        for name, lang, code, bug_lines in CASES:
            code = textwrap.dedent(code).lstrip("\n")
            problems, seconds = check(client, lang, code, bug_lines)
            times.append(seconds)
            if problems:
                print(f"FAIL {name} ({seconds:.1f}s)")
                for p in problems:
                    print(f"  {p}")
            else:
                passed += 1
                print(f"PASS {name} ({seconds:.1f}s)")
    print()
    print(f"{passed}/{len(CASES)} passed")
    print(f"latency: total {sum(times):.1f}s, average {sum(times) / len(times):.1f}s, max {max(times):.1f}s")


if __name__ == "__main__":
    main()
