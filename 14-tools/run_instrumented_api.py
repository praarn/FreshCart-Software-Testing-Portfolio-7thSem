"""Runs the FreshCart backend under coverage.py so the API suite's coverage can be measured.

Usage (from 0-application/backend, test mode env vars set):
    python ../../14-tools/run_instrumented_api.py [port] [coverage_data_file]
Create the file `stop.flag` next to the data file (or press Ctrl+C) to stop the server and write the data.
Then:  coverage report --data-file=<file> --include="app/*"
"""
import sys
import threading
import time
from pathlib import Path

import os
import coverage

sys.path.insert(0, os.getcwd())  # the backend directory, so `app` is importable

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
data = Path(sys.argv[2] if len(sys.argv) > 2 else ".coverage.api").resolve()
flag = data.parent / "stop.flag"
flag.unlink(missing_ok=True)

# SQLAlchemy async runs query code in greenlets; without this coverage stops tracing after the first DB await
cov = coverage.Coverage(branch=True, source=["app"], data_file=str(data), concurrency=["greenlet", "thread"])
cov.start()

import uvicorn  # noqa: E402  (imported after coverage starts so app modules are measured)

server = uvicorn.Server(uvicorn.Config("app.main:app", host="127.0.0.1", port=port, log_level="warning"))


def watch():
    while not flag.exists():
        time.sleep(1)
    server.should_exit = True


threading.Thread(target=watch, daemon=True).start()
try:
    server.run()
finally:
    cov.stop()
    cov.save()
    print("coverage data written to", data)
