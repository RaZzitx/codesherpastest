# menu.py
import threading
import time
from datetime import datetime
import json
import uvicorn

import models
from main import app
import requests
import crud
from database import SessionLocal, engine
from sqlalchemy.orm import Session

# Create database tables
models.Base.metadata.create_all(bind=engine)
# Obtain a database session
db: Session = SessionLocal()

server = None


def readConfig():
    # Read the JSON configuration file
    with open('config.json', 'r') as file:
        config = json.load(file)

    # Extract the fields
    hostConfig = config.get('host')
    portConfig = config.get('port')
    ibanConfig = config.get('iban')

    return hostConfig, portConfig, ibanConfig

def iban_check(iban):
    # Remove spaces and to upper case
    iban = iban.replace(' ', '').upper()

    # Check the length of the Spanish IBAN
    if len(iban) != 24:
        return False

    # Check the country code
    elif not iban.startswith('ES'):
        return False
    else:
        return True

def createAccount(iban, host, port):

    account_data = {
        "iban": iban,  # Reemplaza con el ID de la cuenta correspondiente
        "balance": 0,
    }
    headers = {
        "Content-Type": "application/json"
    }
    requests.post(f"http://{host}:{port}/createAccount", headers=headers, json=account_data)
def getAccountFromIban(iban, host, port):
    createAccount(iban, host, port)
    account = crud.get_account(db, iban)
    return account
def printresponse(response, iban):
    response['date'] = datetime.strptime(response['date'], "%Y-%m-%d %H:%M:%S.%f")
    formatted_date = response['date'].strftime("%d.%m.%Y")

    print("---------- OPERATION SUCCESSFUL ----------")
    print(f"BANK ACCOUNT: {iban}")
    print(f"Date: {formatted_date} Amount: {response['amount']}, Balance: {response['balance']}")

def printTransferResponse(response, originIBAN, destinationIBAN):
    response['date'] = datetime.strptime(response['date'], "%Y-%m-%d %H:%M:%S.%f")
    formatted_date = response['date'].strftime("%d.%m.%Y")

    print("---------- OPERATION SUCCESSFUL ----------")
    print(f"FROM {originIBAN} ----   TO   ---- {destinationIBAN}")
    print(f"Date: {formatted_date} Amount: {response['amount']}, Balance: {response['balance']}")

def printTransactions(data):
    print("------- LIST OF TRANSACTIONS ---------")
    # Print header
    print(f"{'Date':<12} {'Amount':<7} {'Balance':<7}")

    # Sort data by date in descending order (most recent first)
    data.sort(key=lambda x: x['date'], reverse=True)

    # Convert date strings to datetime objects after sorting
    for entry in data:
        entry['date'] = datetime.strptime(entry['date'], "%Y-%m-%d %H:%M:%S.%f")

    # Print each record
    for entry in data:
        formatted_date = entry['date'].strftime("%d.%m.%Y")

        # Format amount with a sign
        amount = f"{entry['amount']:+.0f}"
        print(f"{formatted_date:<12} {amount:<7} {entry['balance']:<7.0f}")
def Deposit(account,amount, host, port):
    transaction_data = {
        "account_id": account.id,  # Reemplaza con el ID de la cuenta correspondiente
        "amount": float(amount),
        "balance": 0,
        "date": ""
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(f"http://{host}:{port}/transactions", headers=headers, json=transaction_data)
    return response
def Withdraw(account,amount, host, port):
    transaction_data = {
        "account_id": account.id,  # Reemplaza con el ID de la cuenta correspondiente
        "amount": -float(amount),
        "balance": 0,
        "date": ""
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(f"http://{host}:{port}/transactions", headers=headers, json=transaction_data)

    return response

def ShowTransactions(account, host, port):
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(f"http://{host}:{port}/transactions/{account.id}", headers=headers)
    return response

# Function to run the Uvicorn server
def run_server(host, port):
    global server
    config = uvicorn.Config(app, host=host, port=port, log_level="error")
    server = uvicorn.Server(config)
    server.run()

# Function to stop the Uvicorn server
def stop_server():
    global server
    if server:
        server.should_exit = True


# Function to show the menu and interact with the server

def show_menu(host, port, iban):
    try:
        while True:
            #iban = input("What is your IBAN? ")
            checkIban = iban_check(iban)

            if checkIban:
                # Remove spaces and to upper case
                iban = iban.replace(' ', '').upper()

                print("\nMenu:")
                print("1. Deposit money")
                print("2. Withdraw money")
                print("3. Transfer money")
                print("4. Show transactions list")
                print("5. Exit")

                # Gets the account item for the input iban
                account = getAccountFromIban(iban, host, port)

                choice = input("Select an option (1/2/3/4/5): ")

                if choice == "1":
                    # Create a transaction
                    try:

                        amount = input("How much do you want to deposit? ")
                        response = Deposit(account, amount, host, port)

                        printresponse(response.json(), iban)

                    except ValueError:
                        print(f"Invalid input: Please enter a valid number.")

                elif choice == "2":
                    try:

                        amount = input("How much do you want to withdraw? ")

                        if account.balance >= float(amount):

                            response = Withdraw(account, amount, host, port)

                            printresponse(response.json(), iban)
                        else:
                            print("You don't have enough money!")

                    except ValueError:
                        print(f"Invalid input: Please enter a valid number.")

                elif choice == "3":
                    try:

                        IBANToTransfer = input("Introduce the IBAN of the transfer: ")
                        checkTransferIban = iban_check(IBANToTransfer)

                        if checkTransferIban:
                            # Remove spaces and to upper case
                            IBANToTransfer = IBANToTransfer.replace(' ', '').upper()

                            if IBANToTransfer != iban:
                                # Gets the account item for the transfer input iban
                                accountToTransfer = getAccountFromIban(IBANToTransfer, host, port)

                                amount = input("How much do you want to transfer? ")
                                if account.balance >= float(amount):

                                    response = Withdraw(account, amount, host, port)
                                    Deposit(accountToTransfer, amount, host, port)

                                    printTransferResponse(response.json(), iban, IBANToTransfer)

                                else:
                                    print("You don't have enough money!")

                            else:
                                print("You can't transfer money to yourself!")
                        else:
                            print("Invalid IBAN try again")
                    except ValueError:
                        print(f"Invalid input: Please enter a valid number.")

                elif choice == "4":
                    response = ShowTransactions(account, host, port)
                    printTransactions(response.json())

                elif choice == "5":
                    print("Exiting the program...")
                    break
                else:
                    print("Invalid option! Try again!")
            else:
                print("Invalid IBAN try again")

    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Exiting...")

if __name__ == "__main__":
    host, port, iban = readConfig()

    # Run the FastAPI server in a separate thread
    server_thread = threading.Thread(target=run_server,args=(host, port), daemon=True)
    server_thread.start()

    # Give the server a moment to start up
    time.sleep(1)

    # Show the menu
    show_menu(host, port, iban)

    # Stop the server
    stop_server()

    # Wait for the server thread to finish
    server_thread.join()
