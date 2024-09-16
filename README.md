# CSC 249 – Project 2 – ATM client with multi-client back-end banking server status report
By Feiran Chang and Liangnuo Zhang  

## (a) which of the P2 design requirements you believe you have satisfied

- Server:  
Our bank server could work well now. It can connect to multiple clients and manipulate messages from clients: It allows sending and receiving multiple messages; validate account number and pin.
We made different status checks for account number and pin validation, and prevent different clients log in to the same account at the same time.

- Client:   
The client also works well. It could manipulate atm work including sending to server and receiving message from server, log in to account, and manage transaction (deposit, withdraw, and get current balance) through keyboard interaction.

- our server and client both handling error including wrong account number, unmatched pin, account logging in another client, wrong transaction type and amount.

- And it could log out/terminate by the request "X" through key board interaction.
- Message Specification Document in ABNF finished

(b) the top 3 most significant knowledge or understanding gaps that are standing in your way 
we haven't revise our code to accept real IP addresses instead of the loopback address
(no other gaps :)

(c) any thoughts you have about what you might do to overcome those gaps 
learn about real IP and modify code. Our basic idea now is to obtain the client IP address instead of the local host and port, and therefore establish a Socket connection to the service using the real IP address and the port number.
