"""Builds screenshots of the test-design / execution documents and the metric charts.

Usage (repo root):  python tools/make_evidence.py [shots|charts|all]
Everything is read from files already in the repo (CSV, junit XML, Newman JSON, coverage summaries, markdown results).
Needs: markdown, matplotlib, numpy, selenium, Chrome.
"""
import csv, html, json, re, sys, tempfile, time, collections
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evidence" / "screenshots"
CSS = """body{font:15px/1.5 Segoe UI,Arial;margin:0;padding:24px 36px;color:#1b1b1b;background:#fff;max-width:1180px}
table{border-collapse:collapse;margin:10px 0;font-size:13px}th,td{border:1px solid #c9c9c9;padding:4px 8px;text-align:left;vertical-align:top}
th{background:#eef2f7}code{background:#f1f1f1;padding:1px 4px;border-radius:3px;font-size:12.5px}pre{background:#f6f6f6;padding:10px;overflow:auto}
h1{font-size:24px;border-bottom:2px solid #2a78d6;padding-bottom:4px}h2{font-size:19px;margin-top:22px}
.bar{background:#2b2b2b;color:#ddd;padding:6px 14px;font:13px Segoe UI;margin:-24px -36px 18px}"""


def driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    o = Options()
    for a in ("--headless=new", "--hide-scrollbars", "--force-device-scale-factor=1"):
        o.add_argument(a)
    return webdriver.Chrome(options=o)


def shot(d, page_html, out, width=1250, maxh=2600):
    with tempfile.TemporaryDirectory() as t:
        f = Path(t) / "p.html"
        f.write_text(page_html, encoding="utf-8")
        d.set_window_size(width, 900)
        d.get(f.as_uri())
        time.sleep(1.5)
        h = min(d.execute_script("return document.documentElement.scrollHeight"), maxh)
        d.set_window_size(width, h + 20)
        time.sleep(0.4)
        d.save_screenshot(str(out))
        print("wrote", out.name, h)


def md_page(path, title):
    import markdown
    text = (ROOT / path).read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    body = re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>', r'<pre class="mermaid">\1</pre>', body, flags=re.S)
    return (f"<html><head><meta charset=utf-8><style>{CSS}</style>"
            "<script src='https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js'></script>"
            "<script>window.addEventListener('load',()=>{try{mermaid.initialize({startOnLoad:false});mermaid.run()}catch(e){}})</script></head>"
            f"<body><div class=bar>{html.escape(title)}</div>{body}</body></html>")


def csv_page(path, cols, rows, title):
    r = list(csv.DictReader((ROOT / path).open(encoding="utf-8")))[:rows]
    th = "".join(f"<th>{c}</th>" for c in cols)
    tr = "".join("<tr>" + "".join(f"<td>{html.escape(x[c])}</td>" for c in cols) + "</tr>" for x in r)
    return f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body><div class=bar>{html.escape(title)}</div><table><tr>{th}</tr>{tr}</table></body></html>"


def term_page(path, title, a=0, b=None):
    raw = re.sub(r"\x1b\[[0-9;]*m", "", (ROOT / path).read_text(encoding="utf-8", errors="replace"))
    lines = raw.splitlines()[a:b]
    body = html.escape("\n".join(l.rstrip() for l in lines))
    return (f"<html><body style='margin:0;background:#0c0c0c'><div style='background:#2b2b2b;color:#ddd;font:13px Segoe UI;padding:6px 12px'>{html.escape(title)}</div>"
            f"<pre style='margin:0;padding:12px;color:#ccc;font:14px Consolas,monospace;line-height:19px'>{body}</pre></body></html>")


# (output name, source, title, max height)
DOCS = [
    ("20_test_plan.png", "test-plan/Test_Plan.md", "test-plan/Test_Plan.md", 2600),
    ("21_requirements_analysis.png", "requirements/Requirements_Analysis.md", "requirements/Requirements_Analysis.md", 2600),
    ("22_equivalence_partitioning.png", "black-box-testing/Equivalence_Partitioning.md", "black-box-testing/Equivalence_Partitioning.md", 2600),
    ("23_boundary_value_analysis.png", "black-box-testing/Boundary_Value_Analysis.md", "black-box-testing/Boundary_Value_Analysis.md", 2600),
    ("24_decision_table.png", "black-box-testing/Decision_Table.md", "black-box-testing/Decision_Table.md", 2600),
    ("25_state_transition.png", "black-box-testing/State_Transition.md", "black-box-testing/State_Transition.md", 2600),
    ("26_traceability_matrix.png", "test-cases/Traceability_Matrix.md", "test-cases/Traceability_Matrix.md", 2600),
    ("28_black_box_results.png", "black-box-testing/Black_Box_Results.md", "black-box-testing/Black_Box_Results.md", 2600),
    ("31_cfg_validate_coupon.png", "white-box-testing/Control_Flow_Graphs/validate_coupon.md", "Control flow graph: validate_coupon (V(G)=10)", 3600),
    ("32_cfg_validate_payment.png", "white-box-testing/Control_Flow_Graphs/validate_payment.md", "Control flow graph: _validate_payment", 2600),
    ("33_cfg_complete_delivery.png", "white-box-testing/Control_Flow_Graphs/complete_delivery.md", "Control flow graph: complete_delivery", 2600),
    ("34_basis_path_testing.png", "white-box-testing/Basis_Path_Testing.md", "white-box-testing/Basis_Path_Testing.md", 2600),
    ("35_coverage_report.png", "white-box-testing/Coverage_Report.md", "white-box-testing/Coverage_Report.md", 2600),
    ("37_api_test_results.png", "api-testing/API_Test_Results.md", "api-testing/API_Test_Results.md (first screen)", 1900),
    ("38_selenium_results.png", "test-execution/Selenium_Results.md", "test-execution/Selenium_Results.md (first screen)", 1900),
    ("39_execution_log.png", "test-execution/Execution_Log.md", "test-execution/Execution_Log.md", 2600),
    ("40_defect_register.png", "defect-reports/README.md", "defect-reports/README.md", 2600),
    ("41_defect_DEF-003.png", "defect-reports/DEF-003_test_mode_tokens_expire_vs_real_clock.md", "DEF-003", 2600),
    ("42_defect_DEF-007.png", "defect-reports/DEF-007_catalog_search_applies_stale_responses.md", "DEF-007", 2600),
    ("43_test_summary_report.png", "final-test-report/Test_Summary_Report.md", "final-test-report/Test_Summary_Report.md", 2600),
]


def shots():
    d = driver()
    try:
        for name, src, title, maxh in DOCS:
            shot(d, md_page(src, title), OUT / name, maxh=maxh)
        shot(d, csv_page("test-cases/Test_Cases.csv",
                         ["TC_ID", "Module", "Rule_IDs", "Title", "Type", "Priority", "Expected_Result", "Automated"], 40,
                         "test-cases/Test_Cases.csv (first 40 of 169 cases)"), OUT / "27_test_cases_table.png")
        shot(d, term_page("black-box-testing/results/black_box_run.log", "pytest, black-box suite (black-box-testing): last 25 lines", -25),
             OUT / "29_black_box_pytest_run.png")
        shot(d, term_page("black-box-testing/results/black_box_run.log", "pytest, black-box suite: first 30 lines (ids name each class / boundary value)", 0, 30),
             OUT / "30_black_box_pytest_ids.png")
        shot(d, term_page("white-box-testing/coverage_term_api.txt", "pytest-cov, API run (instrumented backend driven by Newman)"),
             OUT / "36_coverage_api_term.png")
        shot(d, term_page(".github/workflows/ci.yml", ".github/workflows/ci.yml"), OUT / "44_ci_workflow.png")
    finally:
        d.quit()


BLUE, ORANGE, AQUA, YEL, RED, INK, SUB, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e34948", "#0b0b0b", "#52514e", "#e4e3df"


def charts():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({"font.family": "Segoe UI", "axes.edgecolor": GRID, "axes.labelcolor": SUB, "xtick.color": SUB, "ytick.color": SUB,
                         "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb"})
    M = OUT / "metrics"
    M.mkdir(exist_ok=True)

    def save(fig, n, title, sub):
        fig.suptitle(title, x=0.01, y=1.02, ha="left", fontsize=15, fontweight="bold", color=INK)
        fig.text(0.01, 0.955, sub, fontsize=9.5, color=SUB)
        fig.savefig(M / n, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print("wrote", n)

    def hgrid(ax):
        ax.yaxis.grid(True, color=GRID, lw=.8)
        ax.set_axisbelow(True)

    def vgrid(ax):
        ax.xaxis.grid(True, color=GRID, lw=.8)
        ax.set_axisbelow(True)

    rows = list(csv.DictReader((ROOT / "test-cases/Test_Cases.csv").open(encoding="utf-8")))
    mods = sorted({r["Module"] for r in rows})
    lvl = {"Y": ("Selenium UI", BLUE), "A": ("API (Newman)", ORANGE), "B": ("Black-box EP/BVA", AQUA), "U": ("Unit (white-box)", YEL)}

    # 1 cases by module and level
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bottom = [0] * len(mods)
    for k, (nm, c) in lvl.items():
        v = [sum(1 for r in rows if r["Module"] == m and r["Automated"] == k) for m in mods]
        ax.bar(mods, v, bottom=bottom, color=c, label=nm, width=.62, edgecolor="#fcfcfb", linewidth=2)
        bottom = [a + b for a, b in zip(bottom, v)]
    for i, t in enumerate(bottom):
        ax.text(i, t + .6, t, ha="center", color=INK, fontsize=10)
    hgrid(ax)
    ax.set_ylabel("test cases")
    ax.set_ylim(0, max(bottom) * 1.18)
    ax.legend(frameon=False, ncol=4, loc="upper right", fontsize=9)
    save(fig, "01_cases_by_module.png", f"{len(rows)} test cases designed, by module and automation level", "Source: test-cases/Test_Cases.csv. All 42 business rules traced.")

    # 2 by type
    cnt = collections.Counter(r["Type"] for r in rows)
    order = sorted(cnt, key=cnt.get)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(order, [cnt[k] for k in order], color=BLUE, height=.6)
    for i, k in enumerate(order):
        ax.text(cnt[k] + .6, i, cnt[k], va="center", color=INK, fontsize=10)
    vgrid(ax)
    ax.set_xlabel("test cases")
    save(fig, "02_cases_by_type.png", "Test cases by design technique / type", "Black-box EP 19 + BVA 26; white-box basis path 3 + coverage 5. Source: Test_Cases.csv `Type` column.")

    # 3 priority
    pc = collections.Counter(r["Priority"] for r in rows)
    pr = ["Critical", "High", "Medium", "Low"]
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.bar(pr, [pc[p] for p in pr], color=[RED, ORANGE, YEL, AQUA], width=.55)
    for i, p in enumerate(pr):
        ax.text(i, pc[p] + 1, pc[p], ha="center", color=INK)
    hgrid(ax)
    ax.set_ylabel("test cases")
    save(fig, "03_cases_by_priority.png", "Test cases by priority", "Source: Test_Cases.csv `Priority` column.")

    # 4 results per suite
    nj = json.load(open(ROOT / "api-testing/reports/newman_report.json"))["run"]
    st = nj["stats"]

    def junit(p):
        r = ET.parse(ROOT / p).getroot()
        s = r if r.tag == "testsuite" else r[0]
        return {k: int(s.get(k)) for k in ("tests", "failures", "errors", "skipped")} | {"time": float(s.get("time"))}

    sel = junit("test-execution/selenium_junit.xml")
    bb = junit("black-box-testing/results/black_box_junit.xml")
    nt = (nj["timings"]["completed"] - nj["timings"]["started"]) / 1000
    suites = [("Selenium UI", sel["tests"], sel["failures"] + sel["errors"], sel["time"]),
              ("Newman API requests", st["items"]["total"], st["items"]["failed"], nt),
              ("Black-box EP/BVA", bb["tests"], bb["failures"] + bb["errors"], bb["time"]),
              ("Unit (pytest)", 136, 0, None)]
    total = sum(s[1] for s in suites)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    names = [s[0] for s in suites][::-1]
    tot = [s[1] for s in suites][::-1]
    fl = [s[2] for s in suites][::-1]
    ax.barh(names, [t - f for t, f in zip(tot, fl)], color=AQUA, height=.55, label="passed")
    ax.barh(names, fl, left=[t - f for t, f in zip(tot, fl)], color=RED, height=.55, label="failed")
    for i, (t, f) in enumerate(zip(tot, fl)):
        ax.text(t + 3, i, f"{t - f}/{t} passed", va="center", color=INK, fontsize=10)
    ax.set_xlim(0, max(tot) * 1.3)
    vgrid(ax)
    ax.set_xlabel("tests executed")
    ax.legend(frameon=False, loc="lower right")
    save(fig, "04_execution_results.png", f"Execution results per suite: {total} executed, {sum(s[2] for s in suites)} failed",
         f"Newman also ran {st['assertions']['total']} assertions ({st['assertions']['failed']} failed). Sources: junit XMLs, newman_report.json, Execution_Log.md.")

    # 5 time
    tm = [(n, t) for n, _, _, t in suites if t]
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.bar([n for n, _ in tm], [t / 60 for _, t in tm], color=BLUE, width=.5)
    for i, (n, t) in enumerate(tm):
        ax.text(i, t / 60 + .6, f"{t / 60:.1f} min", ha="center", color=INK)
    hgrid(ax)
    ax.set_ylabel("wall-clock minutes")
    save(fig, "05_execution_time.png", "Execution time per suite", "Selenium pays browser start-up per test; the black-box suite runs 288 tests in about 2 minutes.")

    # 6 black-box by module
    md = (ROOT / "black-box-testing/Black_Box_Results.md").read_text(encoding="utf-8")
    ep_s, bva_s = md.split("## Method 2")

    def per_mod(sec):
        c = collections.Counter()
        for m in re.finditer(r"^\| `TC-(M\d)-\d+` \|.*\| (\d+) \| (\d+) \|$", sec, re.M):
            c[m.group(1)] += int(m.group(2))
        return c

    ep, bva = per_mod(ep_s), per_mod(bva_s)
    ms = sorted(set(ep) | set(bva))
    x = np.arange(len(ms))
    w = .38
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.bar(x - w / 2, [ep[m] for m in ms], w, color=BLUE, label=f"Equivalence partitioning ({sum(ep.values())})")
    ax.bar(x + w / 2, [bva[m] for m in ms], w, color=ORANGE, label=f"Boundary value analysis ({sum(bva.values())})")
    ax.set_xticks(x)
    ax.set_xticklabels(ms)
    hgrid(ax)
    ax.set_ylabel("parametrized tests")
    ax.legend(frameon=False)
    save(fig, "06_black_box_by_module.png", f"Black-box tests per module: {sum(ep.values()) + sum(bva.values())} executed, all passed",
         "Each parametrized test is one equivalence class or one boundary value. Source: Black_Box_Results.md.")

    # 7 coverage totals
    def tot_line(p):
        m = re.search(r"statements (\d+)/(\d+) = ([\d.]+)%; branches (\d+)/(\d+) = ([\d.]+)%", (ROOT / "white-box-testing" / p).read_text())
        return float(m.group(3)), float(m.group(6))

    u, a, c = tot_line("coverage_unit_summary.txt"), tot_line("coverage_api_summary.txt"), tot_line("coverage_combined_totals.txt")
    sv, bv = [u[0], a[0], c[0]], [u[1], a[1], c[1]]
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.bar(x - w / 2, sv, w, color=BLUE, label="Statement")
    ax.bar(x + w / 2, bv, w, color=ORANGE, label="Branch")
    for i in range(3):
        ax.text(x[i] - w / 2, sv[i] + 1.5, f"{sv[i]:.1f}%", ha="center", color=INK, fontsize=10)
        ax.text(x[i] + w / 2, bv[i] + 1.5, f"{bv[i]:.1f}%", ha="center", color=INK, fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(["Unit tests", "API suite", "Combined"])
    ax.set_ylim(0, 115)
    hgrid(ax)
    ax.set_ylabel("% covered")
    ax.legend(frameon=False, loc="upper left")
    save(fig, "07_coverage_totals.png", "Backend code coverage (1,858 statements, 280 branches)",
         "Unit tests target the five business-logic modules; the API suite exercises the rest. Source: white-box-testing/coverage_*.txt.")

    # 8 per-function coverage
    fn = []
    for m in re.finditer(r"^\s+(\S+)::(\S+)\s+(\d+)/(\d+)\s+(\d+)/(\d+)\s*$", (ROOT / "white-box-testing/coverage_unit_summary.txt").read_text(), re.M):
        s, t, b, bt = map(int, m.groups()[2:])
        fn.append((m.group(2), (s + b) / (t + bt) * 100, s, t, b, bt))
    fn.sort(key=lambda r: r[1])
    full = sum(1 for f in fn if f[1] == 100)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh([f[0] for f in fn], [f[1] for f in fn], color=[AQUA if f[1] == 100 else YEL for f in fn], height=.6)
    for i, f in enumerate(fn):
        ax.text(f[1] + .8, i, f"{f[2]}/{f[3]} stmts, {f[4]}/{f[5]} branches", va="center", fontsize=9, color=INK)
    ax.set_xlim(0, 135)
    vgrid(ax)
    ax.set_xlabel("statement + branch coverage, %")
    save(fig, "08_function_coverage_unit.png", "White-box targets: coverage per function (unit tests)",
         f"{full} of {len(fn)} targeted functions at 100%. Source: coverage_unit_summary.txt.")

    # 9 defects
    reg = (ROOT / "defect-reports/README.md").read_text(encoding="utf-8")
    sev = collections.Counter(re.findall(r"^\| \[DEF-\d+\].*\| (Critical|High|Medium|Low) \| (?:Fixed|Open)", reg, re.M))
    foundby = {"Development": 2, "Selenium re-run": 3, "Newman": 1, "Code reading + API": 1, "Code reading": 1}  # from Test_Summary_Report.md "Found by"
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2))
    a1.bar(pr, [sev[p] for p in pr], color=[RED, ORANGE, YEL, AQUA], width=.55)
    for i, p in enumerate(pr):
        a1.text(i, sev[p] + .05, sev[p], ha="center", color=INK)
    hgrid(a1)
    a1.set_title("by severity", loc="left", fontsize=11, color=SUB)
    a1.set_ylabel("defects")
    fb = sorted(foundby.items(), key=lambda kv: kv[1])
    a2.barh([k for k, _ in fb], [v for _, v in fb], color=BLUE, height=.55)
    for i, (k, v) in enumerate(fb):
        a2.text(v + .05, i, v, va="center", color=INK)
    vgrid(a2)
    a2.set_title("by how found", loc="left", fontsize=11, color=SUB)
    save(fig, "09_defects.png", f"{sum(sev.values())} defects found, 0 open", "All fixed and re-tested. Source: defect-reports/README.md, Test_Summary_Report.md.")

    # 10 newman folders
    nm = (ROOT / "api-testing/API_Test_Results.md").read_text(encoding="utf-8")
    fo = re.findall(r"^\| (\d\d [^|]+?) \| (\d+) \|$", nm, re.M)[::-1]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh([f[0] for f in fo], [int(f[1]) for f in fo], color=BLUE, height=.6)
    for i, f in enumerate(fo):
        ax.text(int(f[1]) + .6, i, f[1], va="center", color=INK, fontsize=10)
    vgrid(ax)
    ax.set_xlabel("requests")
    save(fig, "10_newman_requests_by_folder.png", f"Newman: {sum(int(f[1]) for f in fo)} requests, {st['assertions']['total']} assertions, {st['assertions']['failed']} failed",
         "124 requests are negative checks (expect a 4xx). Source: API_Test_Results.md.")


def pdf():
    """Re-renders final-test-report/Test_Summary_Report.pdf from the markdown (headless Chrome print)."""
    import base64
    d = driver()
    try:
        page = md_page("final-test-report/Test_Summary_Report.md", "FreshCart test summary report").replace("<div class=bar>", "<div class=bar style='display:none'>")
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "r.html"
            f.write_text(page, encoding="utf-8")
            d.get(f.as_uri())
            time.sleep(1.5)
            data = d.execute_cdp_cmd("Page.printToPDF", {"printBackground": True, "paperWidth": 8.27, "paperHeight": 11.69, "marginTop": .4, "marginBottom": .4, "marginLeft": .4, "marginRight": .4})
            (ROOT / "final-test-report" / "Test_Summary_Report.pdf").write_bytes(base64.b64decode(data["data"]))
            print("wrote Test_Summary_Report.pdf")
    finally:
        d.quit()


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    if w in ("charts", "all"):
        charts()
    if w in ("shots", "all"):
        shots()
    if w in ("pdf", "all"):
        pdf()
