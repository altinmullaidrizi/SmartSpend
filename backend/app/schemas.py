from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RegisterIn(BaseModel):
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TxnIn(BaseModel):
    description: str
    amount_eur: float
    date: Optional[datetime] = None
    category: Optional[str] = None


class TxnUpdate(BaseModel):
    description: Optional[str] = None
    amount_eur: Optional[float] = None
    category: Optional[str] = None
    date: Optional[datetime] = None


class TxnOut(BaseModel):
    id: int
    user_id: int
    date: datetime
    description: str
    amount_eur: float
    category: Optional[str] = None
    is_anomaly: bool
    source: str
