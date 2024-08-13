from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

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

    # HARCODE A DATE TO MAKE THE TESTS (REPLACE IT IN DB_TRANSACTION -- Date parameter)
    #hardcoded_date = datetime.strptime('2023-08-12 12:34:56.789000', '%Y-%m-%d %H:%M:%S.%f')

    # TO USE TODAY'S TIME (REPLACE IT IN DB_TRANSACTION -- Date parameter)
    '''datetime.utcnow()'''


    new_balance = account.balance + transaction.amount

    db_transaction = models.Transaction(account_id=transaction.account_id, date= datetime.utcnow(), amount=transaction.amount, balance=new_balance, type=transaction.type)
    db.add(db_transaction)
    account.balance = new_balance
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

'''def get_transactions(db: Session, account_id: int, skip: int = 0):
    return db.query(models.Transaction).filter(
        models.Transaction.account_id == account_id).offset(skip).all()'''


# TODO FIX THAT END DATE JUST GETS THE end_date THAT ARE GREATER NOT THE EQUAL ONES
def get_transactions(db: Session, account_id: int, transactionType: int = None, start_date: str = None, end_date: str = None):


    query = db.query(models.Transaction).filter(models.Transaction.account_id == account_id)

    if transactionType is not None:
        query = query.filter(models.Transaction.type == transactionType)

    if start_date is not None:
        print("TRANSACTION DATE: ", start_date)
        query = query.filter(models.Transaction.date >= start_date)

    if end_date is not None:
        print(f"TRANSACTION DATE: {start_date} -- END DATE: {end_date}" )
        query = query.filter(models.Transaction.date <= end_date)

    return query.all()
