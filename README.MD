# TT99 Python Accounting System

This is a Python-based accounting system compliant with Vietnamese Circular 99/2025/TT-BTC.

## Setup

1.  Create and activate a virtual environment:
    `python -m venv venv`
    `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
2.  Install dependencies: `pip install -r requirements.txt`
3.  Set up environment variables in `.env`.
4.  Run the application: `uvicorn app.main:app --reload`

## Notes

*   Ensure `.env` and `venv/` are excluded by `.gitignore`.