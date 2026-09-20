from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.auth import get_current_user
from app.db import get_session
from app.ml.anomaly import is_anomalous
from app.ml.categorizer import predict_category
from app.models import Transaction, User
from app.schemas import TxnIn, TxnOut, TxnUpdate
from app.seed.generate import export_training_csv, generate_transactions

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TxnOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TxnIn,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Let the model pick a category if the user did not choose one.
    category = data.category
    if not category:
        category = predict_category(data.description)

    is_anomaly = False
    if category is not None:
        history_amounts = session.exec(
            select(Transaction.amount_eur).where(
                Transaction.user_id == user.id,
                Transaction.category == category,
            )
        ).all()
        is_anomaly = is_anomalous(data.amount_eur, history_amounts)

    txn = Transaction(
        user_id=user.id,
        date=data.date or datetime.utcnow(),
        description=data.description,
        amount_eur=data.amount_eur,
        category=category,
        is_anomaly=is_anomaly,
        source="manual",
    )
    session.add(txn)
    session.commit()
    session.refresh(txn)
    return txn


@router.get("", response_model=List[TxnOut])
def list_transactions(
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    query = select(Transaction).where(Transaction.user_id == user.id)
    if category is not None:
        query = query.where(Transaction.category == category)
    if date_from is not None:
        query = query.where(Transaction.date >= date_from)
    if date_to is not None:
        query = query.where(Transaction.date <= date_to)
    query = query.order_by(Transaction.date.desc())
    return session.exec(query).all()


def _get_owned_txn(txn_id: int, user: User, session: Session) -> Transaction:
    txn = session.get(Transaction, txn_id)
    if txn is None or txn.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    return txn


@router.patch("/{txn_id}", response_model=TxnOut)
def update_transaction(
    txn_id: int,
    data: TxnUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    txn = _get_owned_txn(txn_id, user, session)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(txn, field, value)
    session.add(txn)
    session.commit()
    session.refresh(txn)
    return txn


@router.delete("/{txn_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    txn_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    txn = _get_owned_txn(txn_id, user, session)
    session.delete(txn)
    session.commit()
    return None


# TODO: add a CSV import endpoint so users can upload a real bank statement
@router.post("/seed")
def seed_transactions(
    n: int = Query(default=200, ge=1),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    txns = generate_transactions(n, user_id=user.id)
    for txn in txns:
        session.add(txn)
    session.commit()
    export_training_csv(txns)
    return {"inserted": n}
