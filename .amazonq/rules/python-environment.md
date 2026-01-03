# Python Environment Rule

## Virtual Environment Usage
- Always use the Python virtual environment located at `.venv/bin/python` for all Python commands
- Use `.venv/bin/pip` for package installations
- Activate virtual environment with `source .venv/bin/activate` when needed
- Never use system Python or global Python installations

## Command Examples
- Use `.venv/bin/python` instead of `python` or `python3`
- Use `.venv/bin/pip` instead of `pip` or `pip3`
- Use `.venv/bin/alembic` for database migrations
- Use `.venv/bin/pytest` for running tests

## Installation Commands
- Create venv: `python3 -m venv .venv`
- Activate: `source .venv/bin/activate`
- Install deps: `.venv/bin/pip install -r requirements.txt`
