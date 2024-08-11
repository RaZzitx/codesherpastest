from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    iban = Column(String, unique=True, index=True)
    balance = Column(Float, default=0.0)
    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    date = Column(String)
    amount = Column(Float)
    balance = Column(Float)
    type = Column(Integer)
    account = relationship("Account", back_populates="transactions")
