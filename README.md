Minimal Flask app

Files added:
- `app.py` — minimal Flask app with `/` and `/api/health` endpoints.
- `requirements.txt` — list of Python packages to install.
- `templates/index.html` — simple HTML for the root route.
- `tests/test_app.py` — a small pytest test using Flask's test client.

Quick start (PowerShell)

1) Activate your venv (PowerShell):

# If execution policy blocks scripts temporarily for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Dot-source the Activate.ps1 so it modifies the current session
. .\.venv\Scripts\Activate.ps1

2) Install dependencies:

pip install -r requirements.txt

3) Run the app:

python app.py

Open http://127.0.0.1:5000 in a browser.

4) Run tests:

pytest -q

Notes
- If PowerShell prevents running `Activate.ps1`, use the Process-scope bypass shown above or set CurrentUser execution policy to RemoteSigned:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force

- You can use `py -3 -m pip install -r requirements.txt` if `pip` is not on PATH.
