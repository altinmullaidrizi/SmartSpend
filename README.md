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
