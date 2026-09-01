# SmartSpend

Personal finance tracker for **Kosovo users** with ML-powered insights.
Built in English, amounts in **EUR (€)**.

Course project — *Seminar and Lab work in Multidisciplinary Application* (UBT).

## What it does

- Track transactions (manual add + seeded Kosovo dataset)
- **Auto-categorize** transactions (ML text classification)
- **Anomaly detection** — flags unusual spending
- **Budget tips** — recommendations grounded in Kosovo price/income levels

## Stack

- Frontend: React
- Backend: Python + FastAPI
- Database: SQLite (Postgres-ready)
- ML: scikit-learn (TF-IDF + LogisticRegression, IsolationForest)
- Auth: JWT + bcrypt

## Running locally

### Backend

```
cd backend
python3 -m venv ../.venv && source ../.venv/bin/activate   # first time only
pip install -r requirements.txt                             # first time only
python -m app.ml.train          # trains and saves the categorizer model (one-time)
uvicorn app.main:app --reload   # runs on http://localhost:8000
```

If a virtualenv already exists at `../.venv`, just run `source ../.venv/bin/activate` instead of creating a new one.

The backend allows cross-origin requests from `http://localhost:5173` (the Vite dev server) via `CORSMiddleware` in `app/main.py`, so the frontend can call it directly during local development.

### Frontend

```
cd frontend
npm install
npm run dev                     # runs on http://localhost:5173
```

Open http://localhost:5173 in a browser, register an account, log in, and optionally click "Load demo data" on the Dashboard to seed 200 realistic Kosovo transactions.

### Frontend tests

```
cd frontend
npm run test -- --run
```
