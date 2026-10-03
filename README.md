# SmartSpend

Personal finance tracker for **Kosovo users** with ML-powered insights.
Built in English, amounts in **EUR (€)**.

Course project for *Seminar and Lab work in Multidisciplinary Application* (UBT).

## What it does

- Track transactions (manual add + seeded Kosovo dataset)
- **Auto-categorize** transactions (ML text classification)
- **Anomaly detection**: flags unusual spending
- **Budget tips**: recommendations grounded in Kosovo price/income levels

## Stack

- Frontend: React
- Backend: Python + FastAPI
- Database: SQLite (set DATABASE_URL to use another database)
- ML: scikit-learn (TF-IDF + LogisticRegression); anomaly detection is a z-score check
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

The API docs (Swagger UI) are at http://localhost:8000/docs.

If a virtualenv already exists at `../.venv`, just run `source ../.venv/bin/activate` instead of creating a new one.

The backend allows cross-origin requests from `http://localhost:5173` (the Vite dev server) via `CORSMiddleware` in `app/main.py`, so the frontend can call it directly during local development.

### Configuration

The backend reads two optional environment variables:

- `SMARTSPEND_SECRET`: secret used to sign JWT tokens. If it is not set, an insecure dev secret is used and a warning is printed at startup. Set it for anything beyond local development.
- `DATABASE_URL`: SQLAlchemy database URL. Defaults to `sqlite:///smartspend.db`.

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

## Using the app

1. **Register** an account with your email and a password, then **log in**.
2. On the Dashboard, click **Load demo data** to add 200 realistic Kosovo transactions.
3. On the Transactions page, add a transaction with a description and amount. Leave the category on **Auto-detect** and the ML model picks one from the description.
4. A red **anomaly** badge means the amount is unusually high or low compared to your past transactions in the same category.
5. The **Insights** page shows budget tips (big increases vs. last month, or spending over 30% of an average Kosovo salary in one category) and a list of all flagged anomalies.
6. To remove a transaction, click **Delete** on its row in the Transactions table.
