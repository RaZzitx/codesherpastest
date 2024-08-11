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


def printTransactions(data, ascending):
    print("------- LIST OF TRANSACTIONS ---------")
    # Print header
    print(f"{'Date':<12} {'Amount':<7} {'Balance':<7} {'Type':<7}")

    # Sort data by date in ascending or descending order based on the 'ascending' flag
    data.sort(key=lambda x: x['date'], reverse=not ascending)

    # Convert date strings to datetime objects after sorting
    for entry in data:
        entry['date'] = datetime.strptime(entry['date'], "%Y-%m-%d %H:%M:%S.%f")

    # Print each record
    for entry in data:
        formatted_date = entry['date'].strftime("%d.%m.%Y")

        if entry['type'] == 0:
            entry['type'] = "Deposit"
        else:
            entry['type'] = "Withdrawal"

        # Format amount with a sign
        amount = f"{entry['amount']:+.0f}"
        print(f"{formatted_date:<12} {amount:<7} {entry['balance']:<7.0f} {entry['type']}")


def Deposit(account, amount, host, port):
    transaction_data = {
        "account_id": account.id,
        "amount": float(amount),
        "balance": 0,
        "date": "",
        "type": int(0)  # DEPOSIT
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(f"http://{host}:{port}/transactions", headers=headers, json=transaction_data)
    return response


def Withdraw(account, amount, host, port):
    transaction_data = {
        "account_id": account.id,
        "amount": -float(amount),
        "balance": 0,
        "date": "",
        "type": 1  # WITHDRAW
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(f"http://{host}:{port}/transactions", headers=headers, json=transaction_data)

    return response
def is_valid_date(date_str):
    """Check if date its in format YYYY-MM-DD."""
    try:
        if date_str:
            datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
def get_user_input():
    # Ask the user if he wants to deposit or withdraw
    transaction_type = input("Do you want to see Deposits or Withdraws? (type 'd' or 'w'): ").strip().lower()
    if transaction_type != 'd' and transaction_type != 'w':
        print("Wrong type of transaction! Will show all transactions.")
        transaction_type = None
    elif transaction_type == 'd':
        transaction_type = 0
    elif transaction_type == 'w':
        transaction_type = 1
    # Ask for start date
    start_date = input("Introduce the start date (YYYY-MM-DD) or press enter in case you don't want: ").strip()
    if start_date == "" or not is_valid_date(start_date):
        start_date = None

    # Ask for end  date
    end_date = input("Introduce the end date (YYYY-MM-DD) or press enter in case you don't want: ").strip()
    if end_date == "" or not is_valid_date(end_date):
        end_date = None
    print("TRANSACTION TYPE: ", transaction_type)
    return transaction_type, start_date, end_date


def ShowTransactions(account, host, port):
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(f"http://{host}:{port}/transactions/{account.id}", headers=headers)
    return response


def build_query_string(transaction_type, start_date, end_date):

    query_params = []

    if transaction_type is not None:
        query_params.append(f"transactionType={transaction_type}")
    if start_date is not None:
        query_params.append(f"start_date={start_date}")
    if end_date is not None:
        query_params.append(f"end_date={end_date}")

    return '&'.join(query_params)

def ShowSearchTransactions(account, host, port, ttype, start_date, end_date):
    headers = {
        "Content-Type": "application/json"
    }
    url = f"http://{host}:{port}/transactions/{account.id}"
    query_string = build_query_string(ttype, start_date, end_date)
    if query_string:
        url += f"?{query_string}"

    print("URL: ", url)
    response = requests.get(url, headers=headers)
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
            # iban = input("What is your IBAN? ")
            checkIban = iban_check(iban)

            if checkIban:
                # Remove spaces and to upper case
                iban = iban.replace(' ', '').upper()

                print("\nMenu:")
                print("1. Deposit money")
                print("2. Withdraw money")
                print("3. Transfer money")
                print("4. Show transactions list")
                print("5. Search movements")
                print("6. Exit")

                # Gets the account item for the input iban
                account = getAccountFromIban(iban, host, port)

                choice = input("Select an option (1/2/3/4/5/6): ")

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
                    sort_order = input(
                        "Do you want to show transactions in ascending or descending order? (a/d) (Enter for default): ").lower()
                    response = ShowTransactions(account, host, port)
                    if sort_order == 'a':
                        printTransactions(response.json(), ascending=True)
                    elif sort_order == 'd':
                        printTransactions(response.json(), ascending=False)
                    else:
                        print("Invalid choice. Showing transactions in descending order by default.")
                        printTransactions(response.json(), ascending=False)

                elif choice == "5":
                    searchSortOrder = input(
                        "Do you want to show transactions in ascending or descending order? (a/d) (Enter for default): ").lower()

                    transactionType, start_date, end_date = get_user_input()
                    response = ShowSearchTransactions(account, host, port, transactionType, start_date, end_date)
                    if response.status_code != 404:

                        if searchSortOrder == 'a':
                            printTransactions(response.json(), ascending=True)
                        elif searchSortOrder == 'd':
                            printTransactions(response.json(), ascending=False)
                        else:
                            print("Invalid choice. Showing transactions in descending order by default.")
                            printTransactions(response.json(), ascending=False)
                    else:
                        print("Transactions not found!")

                elif choice == "6":
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
    server_thread = threading.Thread(target=run_server, args=(host, port), daemon=True)
    server_thread.start()

    # Give the server a moment to start up
    time.sleep(1)

    # Show the menu
    show_menu(host, port, iban)

    # Stop the server
    stop_server()

    # Wait for the server thread to finish
    server_thread.join()
