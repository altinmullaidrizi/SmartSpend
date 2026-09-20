from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.auth import get_current_user
from app.db import get_session
from app.insights.budget import budget_tips, spend_by_category
from app.models import Transaction, User
from app.schemas import TxnOut

router = APIRouter(prefix="/insights", tags=["insights"])


def _month_bounds(dt: datetime):
    # returns (start of this month, start of last month)
    start_of_current = dt.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    if start_of_current.month == 1:
        start_of_previous = start_of_current.replace(
            year=start_of_current.year - 1, month=12
        )
    else:
        start_of_previous = start_of_current.replace(
            month=start_of_current.month - 1
        )
    return start_of_current, start_of_previous


@router.get("/summary")
def summary(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    txns = session.exec(
        select(Transaction).where(Transaction.user_id == user.id)
    ).all()
    total = sum(t.amount_eur for t in txns)
    by_category = spend_by_category(txns)
    return {"total": round(total, 2), "by_category": by_category}


@router.get("/anomalies", response_model=List[TxnOut])
def anomalies(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    query = select(Transaction).where(
        Transaction.user_id == user.id, Transaction.is_anomaly == True  # noqa: E712
    )
    return session.exec(query).all()


@router.get("/tips")
def tips(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    txns = session.exec(
        select(Transaction).where(Transaction.user_id == user.id)
    ).all()
    start_of_current, start_of_previous = _month_bounds(datetime.utcnow())

    current_month_txns = [t for t in txns if t.date >= start_of_current]
    previous_month_txns = [
        t
        for t in txns
        if start_of_previous <= t.date < start_of_current
    ]

    return budget_tips(current_month_txns, previous_month_txns)
