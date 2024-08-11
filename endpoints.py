# app/endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
from database import SessionLocal
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATES A NEW ACCOUNT
@router.post("/createAccount/", response_model=schemas.Account)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = crud.create_account(db=db, account=account)
    if db_account is None:
        raise HTTPException(status_code=400, detail="Account creation failed")
    return db_account


# COMMENTED MIGHT BE USEFUL IN A FUTURE TO GET THE ACCOUNT BY ID

'''@router.get("/accounts/{account_id}", response_model=schemas.Account)
def read_account(account_id: int, db: Session = Depends(get_db)):
    db_account = crud.get_account_byID(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account'''

# MAKES A TRANSACTION (DEPOSIT / WITHDRAW)
@router.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = crud.create_transaction(db=db, transaction=transaction)
    if db_transaction is None:
        raise HTTPException(status_code=400, detail="Transaction failed")
    return db_transaction

# SHOWS THE LIST OF TRANSACTIONS BY ID
@router.get("/transactions/{account_id}", response_model=List[schemas.Transaction])
def read_transactions(account_id: int, db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db, account_id=account_id)
    return transactions
