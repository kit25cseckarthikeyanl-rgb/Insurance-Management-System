# Insurance Management System

A beginner-friendly DBMS academic project built with **Python Flask**, **SQLite**, HTML, and CSS.

## Features
- Dashboard with customer, policy, active-policy, and claim counts
- Customer management: add, view, and delete customers
- Insurance policy management: create, view, and delete policies
- Claims management: submit claims, change claim status, and delete claims
- SQLite relational database with primary keys, foreign keys, and basic constraints
- Responsive dashboard UI and sample records for demonstration

## Tech stack
- Frontend: HTML, CSS, Jinja templates
- Backend: Python + Flask
- Database: SQLite

## Requirements
- Python 3.10 or newer
- pip

## Run locally

### 1. Extract the ZIP and open the project folder
```bash
cd insurance_management_system
```

### 2. Create and activate a virtual environment (recommended)
Windows:
```bash
python -m venv .venv
.venv\\Scripts\\activate
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the application
```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser. The SQLite database (`insurance.db`) and sample records are initialized automatically on the first run.

### Data and secret handling
- `insurance.db` is created locally by the application and is excluded from Git so customer records are not uploaded accidentally.
- The built-in seed records use clearly fictional sample values. Use fictional data only for demonstrations; do not commit real customer information.
- For local development, the app uses a development-only fallback secret. Before deployment, set the `FLASK_SECRET_KEY` environment variable to a securely generated value. Do not store production secrets in source files or commit `.env` files.

PowerShell example (generate a value, then set it for the current terminal session):
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
$env:FLASK_SECRET_KEY = "paste-the-generated-value-here"
```

## Database tables
1. `customers` — customer contact details
2. `policies` — policies linked to customers
3. `claims` — claims linked to policies

Relationships:
- One customer can have multiple policies.
- One policy can have multiple claims.
- Deleting a customer deletes their related policies and claims; deleting a policy deletes its related claims.

## Push to GitHub

Create an empty repository on GitHub, then run these commands inside this project folder:
```bash
git init
git add .
git commit -m "Add Insurance Management System DBMS project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```
Replace `YOUR-USERNAME` and `YOUR-REPOSITORY` with your GitHub details.

## Notes for academic submission
- This is a demonstration project. Use fictional sample data only.
- Before a real deployment, configure a secure secret key, add authentication/authorization, CSRF protection, and stronger validation.
- The application is intended for local academic demonstration, not production insurance processing.
