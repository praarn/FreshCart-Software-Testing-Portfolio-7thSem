"""Renders a saved terminal log as a PNG (dark terminal look) using headless Chrome.

Usage:  python "14-tools/render_terminal_png.py" input.log output.png ["title"] [first_line] [last_line]
The PNG shows the log text unchanged (ANSI colour codes removed); only a line range is selected.
"""
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
    title = sys.argv[3] if len(sys.argv) > 3 else src.name
    lines = re.sub(r"\x1b\[[0-9;]*m", "", src.read_text(encoding="utf-8", errors="replace")).splitlines()
    a = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    b = int(sys.argv[5]) if len(sys.argv) > 5 else len(lines)
    body = html.escape("\n".join(l.rstrip() for l in lines[a:b]))
    height = 60 + 19 * (b - a if b > a else len(lines))
    page = (f"<html><body style='margin:0;background:#0c0c0c'><div style='background:#2b2b2b;color:#ddd;font:13px Segoe UI;padding:6px 12px'>{html.escape(title)}</div>"
            f"<pre style='margin:0;padding:12px;color:#cccccc;font:14px Consolas,monospace;line-height:19px'>{body}</pre></body></html>")
    with tempfile.TemporaryDirectory() as t:
        f = Path(t) / "t.html"
        f.write_text(page, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", f"--screenshot={out}", f"--window-size=1250,{height}", f.as_uri()],
                       check=True, capture_output=True, timeout=120)
    print("wrote", out)


if __name__ == "__main__":
    main()
