# main_testDB.py

from sqlalchemy.orm import Session
import crud
import models
from database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Obtain a database session
db: Session = SessionLocal()




# Create a new account

'''account_create = schemas.AccountCreate(iban="ES7921000813610123455955", balance=190.0)
account = crud.create_account(db=db, account=account_create)
print(f"Account created: {account.iban} -- Balance: {account.balance}")'''

# Remove all the rows on table `accounts`

'''db.query(models.Transaction).delete()
db.commit()'''


# Define the transaction data
'''transaction_data = schemas.TransactionCreate(
    account_id=1,  # Replace with a valid account ID
    amount= 100.0,  # The amount to be added or subtracted from the balance
    balance = 0.0,
    date=datetime.utcnow()  # Optional, will use the current UTC time if not provided
)

# Create the transaction
transaction = crud.create_transaction(db, transaction_data)'''

transactions = crud.get_transactions(db, account_id=1)
print("All transactions:", len(transactions))

for transaction in transactions:
    print(f"ID: {transaction.account_id} DATE: {transaction.date}, amount: {transaction.amount}, balance: {transaction.balance}")
print("###################################################################")

'''account = crud.get_account(db, "ES7921000813610123455955")
print(f"MY ACCOUNT -- ID: {account.id} IBAN: {account.iban}, Balance: {account.balance}")'''

# Obtain all the accounts
accounts = crud.get_accounts(db)
print("All accounts:", len(accounts))
for account in accounts:
    print(f"ID: {account.id} IBAN: {account.iban}, Balance: {account.balance}")

db.close()