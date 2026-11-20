"""Prints totals, per-module and per-function coverage from a `coverage json` file.

Usage:  python "14-tools/coverage_summary.py" cov.json
"""
import json
import sys

TARGETS = {
    "app/services/pricing_service.py": ["validate_coupon", "compute_discount", "compute_delivery_fee", "round2"],
    "app/services/checkout_service.py": ["_validate_payment", "_luhn_ok", "_validate_slot", "_validate_address"],
    "app/services/order_service.py": ["complete_delivery", "admin_advance_status", "cancel_order", "assign_delivery_partner"],
    "app/services/auth_service.py": ["authenticate_user"],
    "app/core/security.py": ["decode_access_token", "create_access_token"],
}


def pct(a, b):
    return "n/a" if not b else f"{100 * a / b:.1f}%"


def main(path):
    d = json.load(open(path, encoding="utf-8"))
    t = d["totals"]
    print(f"TOTAL statements {t['covered_lines']}/{t['num_statements']} = {pct(t['covered_lines'], t['num_statements'])}; "
          f"branches {t['covered_branches']}/{t['num_branches']} = {pct(t['covered_branches'], t['num_branches'])}; "
          f"combined {t['percent_covered']:.1f}%")
    files = {k.replace("\\", "/"): v for k, v in d["files"].items()}
    print("\nPER FUNCTION (statements covered/total; branches covered/total)")
    for f, names in TARGETS.items():
        for n, v in files[f]["functions"].items():
            if n in names:
                s = v["summary"]
                print(f"  {f.split('/')[-1]}::{n}  {s['covered_lines']}/{s['num_statements']}  {s['covered_branches']}/{s['num_branches']}")
    print("\nPER MODULE (services and core)")
    for f, v in sorted(files.items()):
        if f.startswith(("app/services", "app/core", "app/routers", "app/deps", "app/schemas")):
            s = v["summary"]
            print(f"  {f}  stmts {s['covered_lines']}/{s['num_statements']} ({pct(s['covered_lines'], s['num_statements'])})  "
                  f"branches {s['covered_branches']}/{s['num_branches']} ({pct(s['covered_branches'], s['num_branches'])})")


if __name__ == "__main__":
    main(sys.argv[1])
