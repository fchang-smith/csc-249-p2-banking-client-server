#!/usr/bin/env python3
#
# Bank Server application
# Jimmy da Geek

## 1 -> reject
## 0 -> accept

import socket
import selectors
import types

HOST = "127.0.0.1"      # Standard loopback interface address (localhost)
PORT = 65432            # Port to listen on (non-privileged ports are > 1023)
ALL_ACCOUNTS = dict()   # initialize an empty dictionary
ACCT_FILE = "accounts.txt"



##########################################################
#                                                        #
# Bank Server Core Functions                             #
#                                                        #
# No Changes Needed in This Section                      #
#                                                        #
##########################################################

def acctNumberIsValid(ac_num):
    """Return True if ac_num represents a valid account number. This does NOT test whether the account actually exists, only
    whether the value of ac_num is properly formatted to be used as an account number.  A valid account number must be a string,
    lenth = 8, and match the format AA-NNNNN where AA are two alphabetic characters and NNNNN are five numeric characters."""
    return isinstance(ac_num, str) and \
        len(ac_num) == 8 and \
        ac_num[2] == '-' and \
        ac_num[:2].isalpha() and \
        ac_num[3:8].isdigit()

def acctPinIsValid(pin):
    """Return True if pin represents a valid PIN number. A valid PIN number is a four-character string of only numeric characters."""
    return (isinstance(pin, str) and \
        len(pin) == 4 and \
        pin.isdigit())

def amountIsValid(amount):
    """Return True if amount represents a valid amount for banking transactins. For an amount to be valid it must be a positive float()
    value with at most two decimal places."""
    return isinstance(amount, float) and (round(amount, 2) == amount) and (amount >= 0)

class BankAccount:
    """BankAccount instances are used to encapsulate various details about individual bank accounts."""
    acct_number = ''        # a unique account number
    acct_pin = ''           # a four-digit PIN code represented as a string
    acct_balance = 0.0      # a float value of no more than two decimal places
    acct_status = True
    
    def __init__(self, ac_num = "zz-00000", ac_pin = "0000", bal = 0.0):
        """ Initialize the state variables of a new BankAccount instance. """
        if acctNumberIsValid(ac_num):
            self.acct_number = ac_num
        if acctPinIsValid(ac_pin):
            self.acct_pin = ac_pin
        if amountIsValid(bal):
            self.acct_balance = bal

    def deposit(self, amount):
        """ Make a deposit. The value of amount must be valid for bank transactions. If amount is valid, update the acct_balance.
        This method returns three values: self, success_code, current balance.
        Success codes are: 0: valid result; 1: invalid amount given. """
        result_code = 0
        amount = float(amount)
        if not amountIsValid(amount):
            result_code = 1
        else:
            # valid amount, so add it to balance and set succes_code 1
            self.acct_balance += amount
        return self, result_code, round(self.acct_balance,2)

    def withdraw(self, amount):
        """ Make a withdrawal. The value of amount must be valid for bank transactions. If amount is valid, update the acct_balance.
        This method returns three values: self, success_code, current balance.
        Success codes are: 0: valid result; 1: invalid amount given; 2: attempted overdraft. """
        result_code = 0
        amount = float(amount)
        if not amountIsValid(amount):
            # invalid amount, return error 
            result_code = 1
        elif amount > self.acct_balance:
            # attempted overdraft
            result_code = 2
        else:
            # all checks out, subtract amount from the balance
            self.acct_balance -= amount
        return self, result_code, round(self.acct_balance,2)

def get_acct(acct_num):
    """ Lookup acct_num in the ALL_ACCOUNTS database and return the account object if it's found.
        Return False if the acct_num is invalid. """
    if acctNumberIsValid(acct_num) and (acct_num in ALL_ACCOUNTS):
        return ALL_ACCOUNTS[acct_num]
    else:
        return False

def load_account(num_str, pin_str, bal_str):
    """ Load a presumably new account into the in-memory database. All supplied arguments are expected to be strings. """
    try:
        # it is possible that bal_str does not represent a float, so be sure to catch that error.
        bal = float(bal_str)
        if acctNumberIsValid(num_str):
            if get_acct(num_str):
                print(f"Duplicate account detected: {num_str} - ignored")
                return False
            # We have a valid new account number not previously loaded
            pin_str = pin_str[1:]
            new_acct = BankAccount(num_str, pin_str, bal)
            # Add the new account instance to the in-memory database
            ALL_ACCOUNTS[num_str] = new_acct
            print(f"loaded account '{num_str}', with pin '{new_acct.acct_pin}, and balance '{new_acct.acct_balance}")
            return True
    except ValueError:
        print(f"error loading acct '{num_str}': balance value not a float")
    return False
    
def load_all_accounts(acct_file = "accounts.txt"):
    """ Load all accounts into the in-memory database, reading from a file in the same directory as the server application. """
    print(f"loading account data from file: {acct_file}")
    with open(acct_file, "r") as f:
        while True:
            line = f.readline()
            if not line:
                # we're done
                break
            if line[0] == "#":
                # comment line, no error, ignore
                continue
            # convert all alpha characters to lowercase and remove whitespace, then split on comma
            acct_data = line.lower().strip().split(',')
            if len(acct_data) != 3:
                print("ERROR: invalid entry in account file: '{line}' - IGNORED")
                continue
            load_account(acct_data[0], acct_data[1], acct_data[2])
    print("finished loading account data")
    return True
def request_format(request):
    if request[0] == "w" or request[0] == "d":
        if request[1:].isdigit():
            return True
    return False

def analyze_request(request, bank_account):
    if request_format(request):
        if request[0] == "w":
            amt = request[1:]
            result_code = bank_account.withdraw(amt)[1]
            print("result code: " + str(result_code))
            return result_code
        if request[0] == "d":
            amt = request[1:]
            result_code = bank_account.deposit(amt)[1]
            print("result code: " + str(result_code))
            return result_code
    else:
        return False
    
def check_account(acct_num):
    return

def check_pin(acct_pin):
    return
    

##########################################################
#                                                        #
# Bank Server Network Operations                         #
#                                                        #
# TODO: THIS SECTION NEEDS TO BE WRITTEN!!               #
#                                                        #
##########################################################

def run_network_server():
    sel = selectors.DefaultSelector()
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print(f"Listening on {(HOST, PORT)}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(sel, key.fileobj)
                else:
                    service_connection(sel, key, mask)
                
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()

def accept_wrapper(sel, sock):
    conn, addr = sock.accept()  
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(
        valid_code = "11",
        acct_num = None,
        msg = None,
        addr = addr
    )
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(sel, key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        valid_code = data.valid_code
        recv_data = sock.recv(1024)
        recv_data = recv_data.decode("utf-8")
        validation = valid_command(valid_code, recv_data) # check valid_code & r/l
        if validation == 0: # valid_code == 00 & r
            if check_command_format(recv_data): # r;(b/d/w/x);amt(opt)
                data.msg = process_command(recv_data, ALL_ACCOUNTS[data.acct_num]) # r;b/w/d/x;amt/code
            else:
                data.msg = "r;;1" # invalid msg format, does not specify b/d/w/x or invalid amt
        elif validation == 1: # valid_code == 11 & l
            if check_login_format(recv_data): # l;acct_num;pin
                if process_login(recv_data): # login successfully
                    data.acct_num = recv_data.split(";")[1]
                    data.msg = "l;0;0"
                    ALL_ACCOUNTS[data.acct_num].acct_status = False
                else: # wrong acct_num/pin
                    data.msg = "l;1;1"
            else: # wrong login msg format
                data.msg = "l;1;"
        elif validation == 2: # want to do transection before login
            data.msg = ";;1" 
        else: # validation = 3; valid_code == 00  & invalid command
            data.msg = ";;"
    if mask & selectors.EVENT_WRITE:
        if data.msg:
            print(f"Sending {data.msg!r} to {data.addr}")
            data.msg = data.msg.encode("utf-8")
            sent = sock.send(data.msg)
            if (data.msg.decode("utf-8") == ";;1" # want to do transection before login
                or data.msg.decode("utf-8") == "l;1;" # Wrong login msg format
                or data.msg.decode("utf-8") == "l;1;1"): # fail to login
                print(f"Closing connection to {data.addr}")
                sel.unregister(sock)
                sock.close()
            elif data.msg.decode("utf-8") == "r;x;0": # exit request
                ALL_ACCOUNTS[data.acct_num].acct_status = True
                print(f"Closing connection to {data.addr}")
                sel.unregister(sock)
                sock.close()
            else:    
                data.msg = data.msg[sent:]

def process_login(command):
    command = command.split(";")
    ac_num = command[1]
    ac_pin = str(command[2])
    print(ac_num)
    print(ac_pin + " " + len(ac_pin) + " " + type(ac_pin))
    print(get_acct(ac_num).acct_pin + " " + len(get_acct(ac_num).acct_pin) + " " + type(get_acct(ac_num).acct_pin))
    if get_acct(ac_num):
        print("find account")
        if str(get_acct(ac_num).acct_pin) == ac_pin:
            print("pin matches")
            return True
    return False

def check_login_format(command):
    command = command.split(";")
    return acctNumberIsValid(command[1]) and acctPinIsValid(command[2])

def check_command_format(command):
    command = command.split(";")
    check = False
    if len(command) == 3:
        if command[1] == "b" and len(command[2]==0):
            check = True
        if command[1] == "w" and amountIsValid(command[2]):
            check = True
        if command[1] == "d" and amountIsValid(command[2]):
            check = True
        if command[1] == "x" and len(command[2]==0):
            check = True
    return check
        
def process_command(command, account):
    command = command.split(";")
    if command[1] == "b":
        balance = round(account.acct_balance, 2)
        return "r;b;" + str(balance)
    elif command[1] == "w":
        amt = command[2]
        result_code = account.withdraw(amt)[1]
        return "r;w;" + str(result_code)
    elif command[1] == "x":
        return "r;x;0"
    else:
        amt = command[2]
        result_code = account.deposit(amt)[1]
        return "r;d;" + str(result_code)

# int 0 -> valid command (b/d/w); 
# int 1 -> need to login (l);
# int 2 -> no login
# int 3 -> invalid command
def valid_command(valid_code, recv_data): 
    command = recv_data[0]
    if valid_code == "00":
        if command == "r":
            return 0
        else:
            return 3
    else:
        if command == "l":
            return 1
        else:
            return 2

# def service_connection(sel, key, mask):
#     sock = key.fileobj
#     data = key.data
#     if mask & selectors.EVENT_READ:
#         recv_data = sock.recv(1024)  # Should be ready to read
#         recv_data = recv_data.decode("utf-8")
#         if recv_data:
#             if data.valid_code == "11":
#                 strArray = recv_data.split(";")
#                 ac = strArray[0]
#                 pn = strArray[1]
#                 if get_acct(ac):
#                     if get_acct(ac).acct_status == True:
#                         print("Account number is matching!")
#                         data.acct_num = get_acct(ac).acct_number
#                         if pn == ALL_ACCOUNTS[ac].acct_pin:
#                             data.msg = "0"
#                             data.valid_code = "00"
#                             get_acct(ac).acct_status = False
#                             print("PIN is matching!")
#                         else:
#                             print("PIN is not matching")
#                             data.msg = "1"
#                     else:
#                         print("The account is in use")
#                         data.msg = "-2"
#                 else:
#                     print("Account number is not matching")
#                     data.msg = "1"
#             elif data.valid_code == "00":
#                 request = recv_data
#                 if request:
#                     if request_format(request):
#                         result_code= analyze_request(request, ALL_ACCOUNTS[data.acct_num])
#                         if result_code == 1:
#                             result_code == 111
#                         data.msg = str(result_code)
#                     elif request == "b":
#                         data.msg = str(round(ALL_ACCOUNTS[data.acct_num].acct_balance, 2))
#                     elif request == "x":
#                         ALL_ACCOUNTS[data.acct_num].acct_status = True
#                         sel.unregister(sock)
#                         sock.close()
#                     else:
#                         data.msg = "100"         
#     if mask & selectors.EVENT_WRITE:
#         if data.msg:
#             print(f"Sending {data.msg!r} to {data.addr}")
#             data.msg = data.msg.encode("utf-8")
#             sent = sock.send(data.msg)  # Should be ready to write
#             if (data.msg == "1".encode("utf-8")):
#                 print(f"Closing connection to {data.addr}")
#                 ALL_ACCOUNTS[data.acct_num].acct_status = True
#                 sel.unregister(sock)
#                 sock.close()
#             else:    
#                 data.msg = data.msg[sent:]


##########################################################
#                                                        #
# Bank Server Demonstration                              #
#                                                        #
# Demonstrate basic server functions.                    #
# No changes needed in this section.                     #
#                                                        #
##########################################################

def demo_bank_server():
    """ A function that exercises basic server functions and prints out the results. """
    # get the demo account from the database
    acct = get_acct("zz-99999")
    print(f"Test account '{acct.acct_number}' has PIN {acct.acct_pin}")
    print(f"Current account balance: {acct.acct_balance}")
    print(f"Attempting to deposit 123.45...")
    _, code, new_balance = acct.deposit(123.45)
    if not code:
        print(f"Successful deposit, new balance: {new_balance}")
    else:
        print(f"Deposit failed!")
    print(f"Attempting to withdraw 123.45 (same as last deposit)...")
    _, code, new_balance = acct.withdraw(123.45)
    if not code:
        print(f"Successful withdrawal, new balance: {new_balance}")
    else:
        print("Withdrawal failed!")
    print(f"Attempting to deposit 123.4567...")
    _, code, new_balance = acct.deposit(123.4567)
    if not code:
        print(f"Successful deposit (oops), new balance: {new_balance}")
    else:
        print(f"Deposit failed as expected, code {code}") 
    print(f"Attempting to withdraw 12345.45 (too much!)...")
    _, code, new_balance = acct.withdraw(12345.45)
    if not code:
        print(f"Successful withdrawal (oops), new balance: {new_balance}")
    else:
        print(f"Withdrawal failed as expected, code {code}")
    print("End of demo!")

##########################################################
#                                                        #
# Bank Server Startup Operations                         #
#                                                        #
# No changes needed in this section.                     #
#                                                        #
##########################################################

if __name__ == "__main__":
    # on startup, load all the accounts from the account file
    load_all_accounts(ACCT_FILE)
    # uncomment the next line in order to run a simple demo of the server in action
    #demo_bank_server()
    run_network_server()
    print("bank server exiting...")