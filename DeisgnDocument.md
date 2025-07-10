# Country Flag Viewer – Design Document

**Version 1.0 • July 10 2025**

---

## 1 Overview

This design describes how to implement the Country Flag Viewer web application (requirements spec v1.1). The first release (v0.1.0) focuses ---

## 11 Acceptance Criteria for Design

| Ref | Criterion | Verification |
|-----|-----------|--------------|
| AC-D1 | Project bootstraps via `uv pip sync --dev` without errors on Python 3.12. | Run bootstrap script. |
| AC-D2 | `pre-commit run --all-files` reports 0 issues (ruff format/lint, pyright, pytest). | Local + CI logs. |
| AC-D3 | pytest pass rate 100%. | CI job. |
| AC-D4 | `uvicorn app.main:app` renders flag for "Canada" in < 1.5s on localhost with 10 Mbps. | Manual perf smoke test. |
| AC-D5 | Docker image < 150 MB, cold-boot start ≤ 2s. | Build & run timings. |
| AC-D6 | CI workflow completes < 3 min. | GitHub Actions. |
| AC-D7 | README includes quick-start, contribution, and license sections. | Doc review. |g a minimal, production-ready stack with strong automated quality gates.

---

## 2 Technology Stack

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Front-end | FastAPI template engine (Jinja2) + htmx | Keeps everything in Python; htmx gives SPA-like UX without JS build chain. |
| Back-end | FastAPI 0.110 | Async I/O, first-class type hints, OpenAPI autogen. |
| HTTP Client | httpx (async) | Reliable async requests to the flag API. |
| Flag Data Source | REST Countries v3 (fallback: static SVG CDN) | Free, no auth; returns SVG URLs. |
| Packaging / Env | uv (PEP 582 in-place virtual env) | Blazing-fast resolver; produces deterministic lockfile. |
| Type Checking | pyright | Fast static analysis; rich VS Code integration. |
| Lint / Format | ruff | Combines Black-style formatter + lints in one tool. |
| Tests | pytest, pytest-asyncio, httpx.AsyncClient | Friendly async testing + coverage. |
| CI | GitHub Actions + gh CLI | Same commands locally and in CI. |
| Pre-commit | pre-commit with ruff, pyright, pytest hooks | Blocks bad code before commit. |
| Container | Docker (+ uv) | Production parity for deployment (Fly.io / Azure App Service). |


---

## 3 Architecture

```
Browser ─► FastAPI (htmx routes)
                 │
                 ▼
      REST Countries / CDN
```

### Request Flow
1. User submits country name/code via form (GET /?q=canada).
2. FastAPI endpoint validates & normalizes input (ISO code lookup table + fuzzy match).
3. Service fetches flag URL (async) & returns rendered HTML fragment to htmx.
4. htmx swaps fragment into `<div id="flag">…</div>`.

### Other Notes
- **Session History** – maintained client-side; no server state.
- **Caching** – in-memory LRU (64 entries) with 12-hour TTL.

---

## 4 Project Structure

```
country-flag-viewer/
├─ .pre-commit-config.yaml
├─ .github/
│  └─ workflows/ci.yml
├─ app/
│  ├─ __init__.py
│  ├─ main.py          # FastAPI entry
│  ├─ models.py        # pydantic models
│  ├─ services.py      # flag look-up, caching
│  └─ templates/
│      └─ index.html
├─ tests/
│  └─ test_main.py
├─ pyproject.toml      # managed by uv
└─ README.md
```

---

## 5 Key Modules

| Module | Responsibility | Notes |
|--------|----------------|-------|
| app.main | Compose FastAPI app, routes, middleware. | `python -m app.main` entrypoint. |
| app.services | `async def get_flag(country: str) -> FlagMeta` | Handles API call, caching, error mapping. |
| app.models | Pydantic FlagMeta, ErrorResponse | Typed responses for FastAPI. |


---

## 6 Configuration & Tooling

### 6.1 pyproject.toml (excerpt)

```toml
[project]
name = "country-flag-viewer"
version = "0.1.0"
requires-python = ">=3.12"

[project.optional-dependencies]
dev = [
  "ruff",
  "pyright",
  "pytest",
  "pytest-asyncio",
  "httpx",
  "pre-commit"
]

[tool.pyright]
typeCheckingMode = "strict"
reportMissingTypeStubs = "warning"

[tool.ruff]
target-version = "py312"
line-length = 100
lint.select = ["E", "F", "I", "UP", "RUF"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
addopts = "-q --strict-markers --cov=app"
```

Generate lockfile: `uv pip compile -o requirements.lock pyproject.toml`.

### 6.2 Pre-commit

`.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/microsoft/pyright
    rev: v1.1.374
    hooks:
      - id: pyright
        args: ["--project", "pyproject.toml"]
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
```

Enable hooks:

```bash
pre-commit install
```

### 6.3 GitHub Actions CI (.github/workflows/ci.yml)

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install uv
        run: pip install uv
      - name: Install deps
        run: uv pip sync --system requirements.lock
      - name: Run pre-commit
        run: pre-commit run --all-files
```

Local parity: `gh workflow run ci.yml -R <org/repo>` (via gh CLI).

---

## 7 Development Workflow

1. **Clone & bootstrap**
   ```bash
   gh repo clone <org/repo>
   uv venv .venv      # PEP 582 virtual env
   uv pip sync --dev  # dev deps
   pre-commit install
   ```

2. Create a feature branch: `git switch -c feat/<slug>`.
3. Code → `ruff --fix` → pyright passes → pytest.
4. Push → open PR with `gh pr create`.
5. CI must pass; reviewer merges.

---

## 8 Testing Strategy

| Layer | Tooling | Coverage |
|-------|---------|----------|
| Unit | pytest, pytest-asyncio | Input validation, service caching, error mapping. |
| Integration | httpx.AsyncClient (with respx mock) | End-to-end / route hitting mocked flag API. |
| Contract | Diff generated OpenAPI spec vs golden file. | |
| Performance (optional) | locust | Light load test. |


---

## 9 Deployment

### Container

```dockerfile
FROM python:3.12-slim
RUN pip install uv
WORKDIR /src
COPY . .
RUN uv pip sync --system requirements.lock
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Deployment Target
- **Target** – Fly.io (`fly deploy`) or Azure App Service (Docker).
- **Env var** `FLAG_CACHE_TTL=43200` (seconds) for cache control.

---

## 10 Security & Compliance Notes

- HTTPS enforced (HSTS via load balancer).
- CSP header: `default-src 'self'; img-src https:`.
- No cookies / localStorage (no PII).
- Dependabot alerts enabled; renovate optional.

⸻

11  Acceptance Criteria for Design

Ref	Criterion	Verification
AC-D1	Project bootstraps via uv pip sync --dev without errors on Python 3.12.	Run bootstrap script.
AC-D2	pre-commit run --all-files reports 0 issues (ruff format/lint, pyright, pytest).	Local + CI logs.
AC-D3	pytest pass rate 100 %.	CI job.
AC-D4	uvicorn app.main:app renders flag for “Canada” in < 1.5 s on localhost with 10 Mbps.	Manual perf smoke test.
AC-D5	Docker image < 150 MB, cold-boot start ≤ 2 s.	Build & run timings.
AC-D6	CI workflow completes < 3 min.	GitHub Actions.
AC-D7	README includes quick-start, contribution, and license sections.	Doc review.


---

## 12 Future Enhancements (Roadmap)

1. i18n search + autocomplete.
2. Flag download & share link.
3. PWA offline caching.
4. Sentry integration for runtime errors.

---

**End of Design Document**