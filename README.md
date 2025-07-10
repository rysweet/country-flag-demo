# Country Flag Viewer

A minimal FastAPI + htmx web app to view country flags by name or code.  
Implements strong automation, type safety, and CI/CD for production parity.

## Quick Start

```bash
# Clone the repo
gh repo clone rysweet/country-flag-demo
cd country-flag-demo

# Set up environment (Python 3.12+)
uv venv .venv
uv pip sync --dev
pre-commit install

# Run the app
uvicorn app.main:app --reload

# Run tests
pytest
```

## Contribution

- Create a feature branch: `git switch -c feat/<slug>`
- Code, format with `ruff --fix`, check types with `pyright`, and test with `pytest`
- Push and open a PR: `gh pr create`
- Ensure CI passes before requesting review

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.