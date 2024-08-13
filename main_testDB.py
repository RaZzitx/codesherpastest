# main_testDB.py
import random
from datetime import datetime

from sqlalchemy.orm import Session
import crud
import models
import schemas
from database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Obtain a database session
db: Session = SessionLocal()

# Create a new account

'''account_create = schemas.AccountCreate(iban="ES7921000813610123455955", balance=190.0)
account = crud.create_account(db=db, account=account_create)
print(f"Account created: {account.iban} -- Balance: {account.balance}")'''

# Remove all the rows on table `accounts`, change it to Transaction to remove all the `transactions`

'''db.query(models.Account).delete()
db.commit()'''

# Hardcode random transfers to check if the date and type filtering works (it adds + to the withdraw transactions)

'''i = 0
while i < 10:
    # Define the transaction data
    transaction_data = schemas.TransactionCreate(
        account_id=1,  # Replace with a valid account ID
        amount= random.randint(1000, 10000),  # The amount to be added or subtracted from the balance
        balance = 0.0,
        date="",  # Optional, will use the current UTC time if not provided
        type = random.randint(0, 1)
    )

    # Create the transaction
    transaction = crud.create_transaction(db, transaction_data)
    i = i +1'''

# SHOW ALL TRANSACTIONS FILTERING (transactionType = 0 (Deposit), = 1 (Withdrawal), = None (Show all)
transactions = crud.get_transactions(db, account_id=1, transactionType=None, start_date="2023-06-12", end_date="2023-12-12")
print("All transactions:", len(transactions))

for transaction in transactions:
    print(f"ID: {transaction.account_id} DATE: {transaction.date}, amount: {transaction.amount}, balance: {transaction.balance}, type: {transaction.type}")
print("###################################################################")

# GETS THE ACCOUNT BY IBAN

'''account = crud.get_account(db, "ES7921000813610123455955")
print(f"MY ACCOUNT -- ID: {account.id} IBAN: {account.iban}, Balance: {account.balance}")'''

# Obtain all the accounts
accounts = crud.get_accounts(db)
print("All accounts:", len(accounts))
for account in accounts:
    print(f"ID: {account.id} IBAN: {account.iban}, Balance: {account.balance}")

db.close()
