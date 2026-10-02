# PocketSmart AI – Smart Budget & Recommendation Assistant

PocketSmart AI is a FastAPI application for budget planning across three categories:

- Home interior planning
- Party budget planning
- Jewelry recommendation planning

It includes user authentication, SQLite-based recommendation history, and a Gemini-powered planning engine with a safe mock fallback mode.

## Features

- Secure user registration and login
- JWT-style cookie-based session handling
- Protected dashboard and planner pages
- SQLite database for users and recommendation history
- AI-powered recommendations using Gemini when available
- Mock recommendation mode when no API key is available
- Mobile-friendly HTML/CSS/JavaScript frontend

## Project structure

```text
pockat-smart-ai/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── tests/
│   └── test_api.py
└── app/
    ├── __init__.py
    ├── main.py
    ├── config.py
    ├── database.py
    ├── auth.py
    ├── models/
    │   ├── __init__.py
    │   └── schemas.py
    ├── routes/
    │   ├── __init__.py
    │   ├── pages.py
    │   ├── auth.py
    │   └── api.py
    ├── services/
    │   ├── __init__.py
    │   ├── catalog.py
    │   ├── gemini_service.py
    │   └── recommendation_service.py
    ├── static/
    │   ├── css/
    │   │   └── style.css
    │   └── js/
    │       └── app.js
    └── templates/
        ├── base.html
        ├── index.html
        ├── login.html
        ├── register.html
        ├── dashboard.html
        ├── history.html
        ├── home_planner.html
        ├── party_planner.html
        └── jewelry_planner.html
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Create your local environment file from the example and update its values:

   ```powershell
   Copy-Item .env.example .env
   ```

   Generate a unique secret with `.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"` and use it as the `SECRET_KEY` value in `.env`. Keep `.env` local; it is ignored by Git. `.env.example` contains placeholders and is safe to commit.
4. Start the app with Uvicorn.

## Install dependencies

PowerShell:

```powershell
cd "C:\Users\mugil\OneDrive\Documents\pockat-smart-ai"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run app

```powershell
cd "C:\Users\mugil\OneDrive\Documents\pockat-smart-ai"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## Gemini setup

1. Create a Gemini API key in Google AI Studio.
2. Put the key in your local `.env` file, or set `GEMINI_API_KEY` in your deployment provider's environment-variable settings:

```env
GEMINI_API_KEY=your_key_here
MOCK_MODE=false
```

Never commit your real `.env` file or API key. Keep `MOCK_MODE=true` to use demo recommendations without a key. When using Gemini, set `MOCK_MODE=false` and provide `GEMINI_API_KEY`.

## Testing

```powershell
cd "C:\Users\mugil\OneDrive\Documents\pockat-smart-ai"
.\.venv\Scripts\python.exe -m pytest -q
```
