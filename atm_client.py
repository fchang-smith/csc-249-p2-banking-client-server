#!/usr/bin/env python3
#
# Automated Teller Machine (ATM) client application.

## 1 -> reject
## 0 -> accept

import socket
import selectors

HOST = "127.0.0.1"      # The bank server's IP address
PORT = 65432            # The port used by the bank server

##########################################################
#                                                        #
# ATM Client Network Operations                          #
#                                                        #
# NEEDS REVIEW. Changes may be needed in this section.   #
#                                                        #
##########################################################
def configure_selectors(sock):
    sock.setblocking(False)
    sel = selectors.DefaultSelector()
    events = selectors.EVENT_WRITE | selectors.EVENT_READ
    data = {}
    sel.register(sock, events, data=data)
    return sel

def send_to_server(sel, msg):
    """ Given an open socket connection (sock) and a string msg, send the string to the server. """
    for key, mask in sel.select():
        sock = key.fileobj
        if mask & selectors.EVENT_WRITE:
            print("Sending " + msg + " to the server...")
            return sock.sendall(msg.encode('utf-8'))
        
        else:
            print("It is not ready to send massage")
            return False

def get_from_server(sel):
    """ Attempt to receive a message from the active connection. Block until message is received. """
    while True:
        for key, mask in sel.select():
            sock = key.fileobj
            if mask & selectors.EVENT_READ:
                msg = sock.recv(1024)
                if msg:
                    return msg.decode("utf-8")

# 11 -> needs to terminate the program
# 01 -> wrong input format, but allow to try again
# d0 -> deposit ok
# d1 -> deposit invalid amount
# b0 -> balance ok
# w0 -> withdraw ok
# w1 -> withdraw invalid amt
# w2 -> withdraw overdraft
# l0 -> login ok
def analyze_reply(msg):
    if msg == "r;;1":
        print("invalid msg format, does not specify b/d/w/x or invalid amt")
        return "00"
    elif msg == "l;1;1":
        print("Account number and PIN do not match. Terminating ATM session.")
        return "11"
    elif msg == "l;1;":
        print("wrong login msg format")
        return "11"
    elif msg == ";;1":
        print("want to do transection before login")
        return "11"
    elif msg == "l;0;0":
        print("Thank you, your credentials have been validated.")
        return "l0"
    elif msg == "l;2;":
        print("The account is in use! Terminating ATM session")
        return "11"
    elif msg == ";;":
        print("wrong input format, does not specify r/l")
        return "00"
    elif msg[:4] == "r;b;" and msg[4:].isnumeric():
        print("successful get balance: " + msg[4:])
        return "b0"
    elif msg[:4] == "r;w":
        if msg[4:] == "0":
            print("successfully withdraw")
            return "w0"
        elif msg[4:] =="1":
            print("invalid amount")
            return "w1"
        else:
            print("overdraft account")
            return "w2"
    elif msg[0:4] == "r;d;":
        if msg[4:] == "0":
            print("successfully deposit")
            return "d0"
        else:
            print("invalid amount")
            return "d1"
    elif msg == "r;x;0":
        print("exit!")
        return "11"
    else:
        print("reply not recognizable")
        return "11"

def login_to_server(sel, acct_num, pin):
    """ Attempt to login to the bank server. Pass acct_num and pin, get response, parse and check whether login was successful. """
    sent = "l;" + acct_num + ";" + pin
    send_to_server(sel, sent)
    msg = get_from_server(sel)
    return analyze_reply(msg)
    

def get_login_info():
    """ Get info from customer. Validate inputs, ask again if given invalid input. """
    acct_num = input("Please enter your account number: ")
    if isinstance(acct_num, str) and \
    len(acct_num) == 8 and \
    acct_num[2] == '-' and \
    acct_num[:2].isalpha() and \
    acct_num[3:8].isdigit():
        pin = input("Please enter your four digit PIN: ")
        if (isinstance(pin, str) and \
        len(pin) == 4 and \
        pin.isdigit()):   
            return acct_num, pin
        else:
            print("The PIN format is invalid")
    else:
        print("The account number is in invalid format")
    return "", ""

def process_deposit(sel, acct_num):
    """ Write this code. """
    amt = input()
    # communicate with the server to request the deposit, check response for success or failure.
    send_to_server(sel, "r;d;" + amt)
    reply = get_from_server(sel)
    code = analyze_reply(reply)
    if code == "d0":
        print("Deposit transaction completed.")
        bal = get_acct_balance(sel, acct_num)
        print("Your new balance is "+ bal)
    else:
        print("Invalid amount")
    return

def get_acct_balance(sel, acct_num):
    """ Ask the server for current account balance. """
    send_to_server(sel, "r;b;")
    reply = get_from_server(sel)
    code = analyze_reply(reply)
    if code == "b0":
    # code needed here, to get balance from server then return it
        return reply[4:]

def process_withdrawal(sel, bal, acct_num):
    """ Write this code. """
    amt = input()
    #  communicate with the server to request the withdrawal, check response for success or failure.
    if amt>bal:
        print("The amount to withdraw is more than your balance")
        return 
    send_to_server(sel, "r;w;" + amt)
    reply = get_from_server(sel)
    code = analyze_reply(reply)
    if code == "w0":
        print("Withdrawal transaction completed.")
        bal = get_acct_balance(sel, acct_num)
        print("Your new balance is " + bal)
    elif code == "w1":
        print("Invalid amount")
    else:
        print("Account overdraft")
    return

def process_customer_transactions(sel, acct_num):
    """ Ask customer for a transaction, communicate with server. Revise as needed. """
    while True:
        bal = get_acct_balance(sel, acct_num)
        print("Select a transaction. Enter 'd' to deposit, 'w' to withdraw, or 'x' to exit.")
        req = input("Your choice? ").lower()
        if req not in ('d', 'w', 'x'):
            print("Unrecognized choice, please try again.")
            continue
        if req == 'x':
            send_to_server(sel, "r;x;")
            # if customer wants to exit, break out of the loop
            break
        elif req == 'd':
            print(f"How much would you like to deposit? (You have ${bal} available)")
            process_deposit(sel, acct_num)
        else:
            print(f"How much would you like to withdraw? (You have ${bal} available)")
            process_withdrawal(sel, bal, acct_num)

def run_atm_core_loop(sock):
    sel = configure_selectors(sock)
    """ Given an active network connection to the bank server, run the core business loop. """
    login_check = False
    acct_num, pin = get_login_info()
    if acct_num != "" and pin != "":
        login_check = True
    if login_check:
        validated = login_to_server(sel, acct_num, pin)
        if validated == "11":
            sock.close()
            return False
        process_customer_transactions(sel, acct_num)
        sock.close()
        print("ATM session terminating.")
        return True
    else:
        sock.close()
        print("ATM session terminating.")

##########################################################
#                                                        #
# ATM Client Startup Operations                          #
#                                                        #
# No changes needed in this section.                     #
#                                                        #
##########################################################

def run_network_client():
    """ This function connects the client to the server and runs the main loop. """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            run_atm_core_loop(s)
    except Exception as e:
        print(f"Unable to connect to the banking server - exiting...")

if __name__ == "__main__":
    print("Welcome to the ACME ATM Client, where customer satisfaction is our goal!")
    run_network_client()
    print("Thanks for banking with us! Come again soon!!")