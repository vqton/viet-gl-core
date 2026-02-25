AGENTS.md

Overview
- This file provides guidance for agentic contributors working in this repository.
- It covers build, lint, test commands, and code style guidelines to ensure consistent, maintainable work.
- If there are Cursor rules (in .cursor/rules/ or .cursorrules) or Copilot rules (in .github/copilot-instructions.md), include them here.

1) Build / Lint / Test workflow
Setup
- Create a fresh Python environment to isolate dependencies.
  - Unix-like: `python3 -m venv venv` then `source venv/bin/activate`.
  - Windows: `python -m venv venv` then `.\\venv\\Scripts\\activate`.
- Dependency installation:
  - If a requirements.txt exists: `pip install -r requirements.txt`.
  - Otherwise: install common tools manually: `pip install pytest flake8 mypy black isort`.
- Ensure Python version compatibility (prefer Python 3.8+).

Commands to run
- Build / install the package (if a setup is present):
  - `pip install -e .`  # editable install
- Run all tests:
  - `pytest -q`
- Run a single test:
  - `pytest tests/path/to/file.py::TestClass::test_name -q`
- Run tests with coverage (optional):
  - `pytest --maxfail=1 --disable-warnings -q --cov=src --cov-report=term-missing`
- Lint the codebase:
  - `flake8`  # style + logical errors
  - `isort . --check-only --diff`  # import sorting
  - `black --check .`  # formatting
- Type checks:
  - `mypy src tests`  # or adjust path to your code
- Run a combined quality sweep:
  - `pytest -q && flake8 && isort . --check-only --diff && black --check . && mypy src tests`

Single test examples
- To run a focused test you can use:
  - `pytest tests/test_example.py::TestFeature.test_case`.
- Use -k for keyword selection: `pytest -k "featureA and not slow" -q`.

2) Code style guidelines
General
- Follow a single, consistent style across the codebase to minimize churn.
- Prefer explicit, readable code over clever tricks.
- Keep dependencies pinned in requirements.txt or pyproject.toml to stable builds.

3) Language and formatting rules
Imports
- Structure: standard library imports, blank line, third-party imports, blank line, local imports.
- Avoid wildcard imports (from module import *).
- Use absolute imports where possible; prefer package level imports.
- Run isort to enforce ordering; rely on it in CI.

Formatting
- Adopt Black as the canonical formatter. Use the default configuration (88 chars) unless project guidelines specify otherwise.
- Do not format by hand; let Black handle formatting differences.
- Keep lines reasonably short; wrap long strings with implicit concatenation or parentheses.

Typing
- Turn on type hints where they add clarity; annotate public APIs.
- Use `from __future__ import annotations` at the top of modules to enable postponed evaluation of annotations.
- Import common typing helpers: `List`, `Dict`, `Optional`, `Tuple`, `Union`, `Protocol`, `TypedDict` as appropriate.
- For functions that can raise specific exceptions, declare return types and exceptions as needed.

Naming conventions
- Functions and variables: snake_case.
- Classes: CamelCase.
- Constants: ALL_CAPS.
- Exceptions: end with `Error` or `Exception` (e.g., `ValidationError`).
- Private/internal helpers: prefix with underscore.

Docstrings and comments
- Public modules/classes/functions should have docstrings.
- Docstrings should describe purpose, arguments, return values, and side effects.
- Use a consistent style: Google-style or NumPy-style; pick one and apply project-wide.
- Avoid obvious comments; prefer self-documenting code and targeted clarifications when necessary.

Error handling
- Do not swallow exceptions; catch only what you can handle meaningfully.
- Avoid bare `except:`; catch specific exceptions.
- Add context to error messages; include relevant values when possible.
- When a library crosses boundary boundaries (public API), translate low-level errors into meaningful, typed exceptions.

Logging
- Use module-level logger: `logger = logging.getLogger(__name__)`.
- Log at appropriate levels: debug for verbose, info for normal progress, warning/error for issues.
- Do not leak sensitive information in logs.

Tests
- Tests live under `tests/` with file names like `test_*.py`.
- Test classes should start with `Test` and contain test methods `test_*`.
- Use fixtures for setup/teardown; prefer function-scoped fixtures unless sharing is needed.
- Name tests descriptively; avoid generic names like `test_it_works` unless they truly describe behavior.
- Parameterize tests where appropriate to cover multiple inputs.
- Mock external systems carefully; restore state in teardown.

CI and tooling
- CI should run: install, lint, type-check, and tests on every push/PR.
- Include caching or artifacts as appropriate for speed.
- Fail early on lint/type/test failures to guide quick fixes.

Cursor rules
- Cursor rules (if present) should be respected when generating code or edits.
- If there are no Cursor rules, note that explicitly and proceed with standard edits.

Copilot rules
- Copilot instructions (if present) should be followed verbatim for safety and compliance.
- If not present, proceed with caution and human-reviewed changes.

Agent workflow tips
- Make small, targeted edits; run tests locally when possible.
- Prefer patching a single file at a time when introducing new features.
- Include a short rationale in commit messages describing why the change was made.
- When unsure, draft two or three minimal changes and run the relevant tests to confirm expectations.

Appendix: example commands
- Activate env: `source venv/bin/activate` or `.
venv\Scripts\activate`.
- Install: `pip install -r requirements.txt`.
- Run a single test: `pytest tests/test_module.py::TestCase.test_method -q`.
- Lint: `flake8` and `black --check .`.
- Type: `mypy src tests`.
