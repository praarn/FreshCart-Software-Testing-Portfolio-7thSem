"""Checks that the counts quoted in docs match the tools' own output.

Usage (from the repo root):   python tools/consistency_check.py
Needs: the committed CSV, newman_report.json and junit results; optionally pytest for the unit count.
Exits 1 if any quoted number differs from the source of truth.
"""
import csv
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [p for p in ROOT.rglob("*.md") if not any(x in p.parts for x in ("node_modules", ".git", "coverage_html", ".next"))]
fails = []


def truth():
    rows = list(csv.DictReader(open(ROOT / "Test_Case_Design" / "Test_Cases.csv", encoding="utf-8", newline="")))
    t = {"cases": len(rows)}
    c = Counter(r["Automated"] for r in rows)
    t.update(selenium=c["Y"], api=c["A"], unit=c["U"], manual=c["N"], blackbox=c["B"])
    nm = json.load(open(ROOT / "API_Testing" / "reports" / "newman_report.json", encoding="utf-8"))
    ex = {e["item"]["id"]: e for e in nm["run"]["executions"]}
    t["api_requests"] = len(ex)
    t["assertions"] = nm["run"]["stats"]["assertions"]["total"]
    t["assertions_failed"] = nm["run"]["stats"]["assertions"]["failed"]
    t["rules"] = len(re.findall(r"^\| (R\d\.\d) \|", (ROOT / "Application/docs/REQUIREMENTS.md").read_text(encoding="utf-8"), flags=re.M))
    return t


def check(label, pattern, expected, files=None):
    """Every match of pattern (group 1 = the number) in the docs must equal expected."""
    seen = []
    pattern = re.compile(pattern)
    for p in files or DOCS:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in pattern.finditer(text):
            g = next((x for x in m.groups() if x), None)
            if g is not None:
                seen.append((p.relative_to(ROOT).as_posix(), int(g)))
    bad = [(f, n) for f, n in seen if n != expected]
    print(f"{'FAIL' if bad else 'ok  '} {label}: expected {expected}, {len(seen)} mentions" + (f", mismatches {bad}" if bad else ""))
    if bad:
        fails.append(label)


def main():
    t = truth()
    print("source of truth:", t)
    check("test cases total", r"\b(\d+) (?:test cases|cases designed|test case specifications)\b|designed \| (\d+) \(", t["cases"])
    check("business rules", r"\b(\d+) (?:business rules|rules \(R|rules, all)", t["rules"])
    check("selenium automated cases", r"\b(\d+) (?:Selenium|automated Selenium) (?:cases|tests)\b", t["selenium"])
    check("api requests", r"\b(\d+) requests,? (?:and )?\d+ assertions|Newman \((\d+) requests", t["api_requests"])
    check("api assertions", r"\b(\d+) assertions\b", t["assertions"], [p for p in DOCS if p.name in ("README.md", "Conclusion.md", "Demo_Script.md", "Viva_QA.md")])
    if t["assertions_failed"]:
        fails.append("newman has failed assertions")
    r = subprocess.run([sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider"], cwd=ROOT / "Application/backend", capture_output=True, text=True)
    m = re.search(r"(\d+) tests? collected", r.stdout)
    t["unit_tests"] = int(m.group(1)) if m else -1
    print("unit tests collected:", t["unit_tests"])
    check("unit tests", r"(?<![\w-])(\d+) (?:unit tests|pytest tests)|[Uu]nit tests? \((\d+)\)|[Uu]nit tests \| (\d+) passed", t["unit_tests"])
    # every non-Selenium case must be referenced by the Newman collection (A) or a unit test (U)
    coll = (ROOT / "API_Testing" / "FreshCart.postman_collection.json").read_text(encoding="utf-8")
    units = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "Application/backend/tests/unit").glob("*.py"))
    for r in csv.DictReader(open(ROOT / "Test_Case_Design" / "Test_Cases.csv", encoding="utf-8", newline="")):
        src = {"A": coll, "U": units}.get(r["Automated"])
        if src is not None and r["TC_ID"] not in src:
            print("FAIL no test references", r["TC_ID"], r["Automated"])
            fails.append(r["TC_ID"])
    # every black-box technique case (B) is referenced by a test in Black_Box_Testing
    bb = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "Black_Box_Testing/tests").glob("test_*.py"))
    bb_missing = [r["TC_ID"] for r in csv.DictReader(open(ROOT / "Test_Case_Design" / "Test_Cases.csv", encoding="utf-8", newline="")) if r["Automated"] == "B" and r["TC_ID"] not in bb]
    print("FAIL black-box cases without a test:" if bb_missing else "ok   every black-box case has a test", bb_missing or "")
    if bb_missing:
        fails.append("black-box links")
    bb_junit = ROOT / "Black_Box_Testing" / "results" / "black_box_junit.xml"
    if bb_junit.exists():
        s = re.search(r'<testsuite [^>]*', bb_junit.read_text(encoding="utf-8")).group(0)
        n, f_, e_ = (int(re.search(rf'{k}="(\d+)"', s).group(1)) for k in ("tests", "failures", "errors"))
        t["blackbox_tests"] = n
        print(f"black-box suite: {n} tests, {f_} failures, {e_} errors")
        check("black-box tests run", r"\b(\d+) black-box tests\b|[Bb]lack-box[^|\n]*\| (\d+) (?:passed|executed)", n)
        if f_ or e_:
            fails.append("black-box suite has failures")
    # every Selenium case has a test with its ID in the docstring
    tests = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "Test_Automation/tests").glob("test_*.py"))
    missing = [r["TC_ID"] for r in csv.DictReader(open(ROOT / "Test_Case_Design" / "Test_Cases.csv", encoding="utf-8", newline="")) if r["Automated"] == "Y" and r["TC_ID"] not in tests]
    print("FAIL selenium cases without a test:" if missing else "ok   every Selenium case has a test", missing or "")
    if missing:
        fails.append("selenium links")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
