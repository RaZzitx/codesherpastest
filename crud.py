from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime
from sqlalchemy.exc import IntegrityError

def create_account(db: Session, account: schemas.AccountCreate):
    db_account = models.Account(iban=account.iban, balance=account.balance)
    db.add(db_account)
    try:
        db.commit()
        db.refresh(db_account)
        print("IBAN ADDED TO THE DATABASE")

    except IntegrityError:
        db.rollback()
        print("IBAN DETECTED IN THE DATABASE")
        return None
    return db_account

def get_account_byID(db: Session, account_id: id):
    return db.query(models.Account).filter(models.Account.id == account_id).first()

# GET ACCOUNT BY IBAN
def get_account(db: Session, iban: str):
    account = db.query(models.Account).filter(models.Account.iban == iban).first()
    if not account:
        return None
    return account

# GET ALL THE ACCOUNTS
def get_accounts(db: Session, skip: int = 0):
    return db.query(models.Account).offset(skip).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate):

    account = db.query(models.Account).filter(models.Account.id == transaction.account_id).first()
    if not account:
        return None


    new_balance = account.balance + transaction.amount

    db_transaction = models.Transaction(account_id=transaction.account_id, date=datetime.utcnow(), amount=transaction.amount, balance=new_balance)
    db.add(db_transaction)
    account.balance = new_balance
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, account_id: int, skip: int = 0):
    return db.query(models.Transaction).filter(
        models.Transaction.account_id == account_id).offset(skip).all()
