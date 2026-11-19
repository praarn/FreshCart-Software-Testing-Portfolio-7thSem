# Commands — running FreshCart on any OS

All commands assume you're starting from the repo root (`Software-Testing-Portfolio/`).
Pick **one** of: local (SQLite, two terminals, no external services) or Docker Compose
(Postgres, one command). Local is faster to iterate on; Docker is closer to a real deploy
and is what CI-equivalent `docker compose up` verification uses.

Full explanation of what's being run: [`0. application/explanation.md`](0.%20application/explanation.md).
Seed credentials and test-mode env vars: [`0. application/README.md`](0.%20application/README.md).

---

## Prerequisites

- Python 3.11+ (3.12 recommended — see the note below if you're on a brand-new Python
  release and `pip install` fails building wheels)
- Node.js 20+
- Docker Desktop (only if using the Docker Compose path)

> **Python version note:** on a very recently released Python (e.g. 3.14 at the time this
> was built), some pinned dependencies may not yet publish prebuilt wheels, and building
> them from source can fail. If `pip install -r requirements.txt` fails with a build error,
> install a 3.12.x interpreter and create the virtual environment with that instead
> (`py -3.12 -m venv .venv` on Windows, `python3.12 -m venv .venv` elsewhere).

---

## Option A — Local (SQLite, zero external services)

### macOS / Linux (bash or zsh)

```bash
# Backend — terminal 1
cd "0. application/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

```bash
# Frontend — terminal 2
cd "0. application/frontend"
npm install
npm run dev
```

### Windows — PowerShell

```powershell
# Backend — terminal 1
cd Application\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

```powershell
# Frontend — terminal 2
cd Application\frontend
npm install
npm run dev
```

> If `Activate.ps1` is blocked by execution policy, either run PowerShell as the same user
> and execute `Set-ExecutionPolicy -Scope Process RemoteSigned` first, or use
> `.venv\Scripts\activate.bat` from `cmd.exe` instead.

### Windows — cmd.exe

```bat
cd Application\backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

```bat
cd Application\frontend
npm install
npm run dev
```

### Windows — Git Bash

Identical to the macOS/Linux block above, except the venv activation path uses `Scripts`:

```bash
cd "0. application/backend"
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

### Once both are running

- Backend: http://localhost:8000 — Swagger UI at http://localhost:8000/docs
- Frontend: http://localhost:3000

---

## Option B — Docker Compose (Postgres + backend + frontend)

Identical on every OS once Docker Desktop is installed and running:

```bash
docker compose up --build
```

Add `-d` to run detached. This builds both images, starts Postgres, waits for it to be
healthy, runs Alembic migrations and the seed script inside the backend container, and
serves backend on `:8000` and frontend on `:3000`.

```bash
docker compose ps          # check container status
docker compose logs -f     # follow logs from all three services
docker compose down        # stop and remove the containers
```

---

## Running in test mode (deterministic, for automated test suites)

Setting `APP_ENV=test` mounts `POST /api/test/reset` (wipe + reseed). Setting `FIXED_NOW`
freezes the backend's clock so delivery-slot and weekday-coupon rules are deterministic.
These only need to be set for the **backend** process.

**macOS / Linux / Git Bash:**

```bash
APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 uvicorn app.main:app --reload
```

**Windows PowerShell:**

```powershell
$env:APP_ENV = "test"
$env:FIXED_NOW = "2026-11-10T09:00:00"
uvicorn app.main:app --reload
```

**Windows cmd.exe:**

```bat
set APP_ENV=test
set FIXED_NOW=2026-11-10T09:00:00
uvicorn app.main:app --reload
```

**Docker Compose:** set `APP_ENV` and `FIXED_NOW` under the `backend` service's
`environment:` block in `docker-compose.yml` before running `docker compose up --build`.

Once running in test mode, reset to a known state with:

```bash
curl -X POST http://localhost:8000/api/test/reset
```

With the backend in test mode, the black-box suite (equivalence partitioning and boundary value analysis, about 3 minutes)
runs the same way on every OS:

```bash
cd black-box-testing
pip install -r requirements.txt
pytest --junitxml=results/black_box_junit.xml     # then: python make_results.py
```

It talks to `http://127.0.0.1:8000/api` (set `FRESHCART_API_URL` for another address; `127.0.0.1` rather than
`localhost` on purpose, because on Windows `localhost` tries IPv6 first and stalls every request).

---

## Other useful commands

```bash
# Backend: run the unit tests (white box: basis path and coverage cases)
cd "0. application/backend" && pytest

# Backend: create a new migration after changing a model
cd "0. application/backend" && alembic revision --autogenerate -m "describe the change"

# Frontend: production build (what CI runs; also what the Docker image builds)
cd "0. application/frontend" && npm run build

# Frontend: lint
cd "0. application/frontend" && npm run lint
```
