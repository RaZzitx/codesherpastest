from pydantic import BaseModel
from typing import List

class TransactionBase(BaseModel):
    date: str
    amount: float
    balance: float
    type: int
class TransactionCreate(TransactionBase):
    account_id: int

class Transaction(TransactionBase):
    id: int


    class Config:
        from_attributes = True

class AccountBase(BaseModel):
    iban: str
    balance: float

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    transactions: List[Transaction] = []

    class Config:
        from_attributes = True
