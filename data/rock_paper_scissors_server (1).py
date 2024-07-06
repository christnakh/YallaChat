import socket
import threading
import random

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creating stream socket

server.bind((socket.gethostbyname(socket.gethostname()), 5050))  # binding the server


def handle_client(connection, address):
    while True:  # we keep playing with the server until client sends message DISCONNECT
        msg = connection.recv(1024).decode('utf-8')
        if msg == "DISCONNECT":
            break
        server_output = random.choice(["rock", "paper", "scissors"])
        if server_output == msg:
            connection.send("It's a Tie!".encode('utf-8'))
        elif server_output == "rock":
            if msg == "paper":
                connection.send("You Win!".encode('utf-8'))
            else:
                connection.send("You Lose!".encode('utf-8'))
        elif server_output == "paper":
            if msg == "scissors":
                connection.send("You Win!".encode('utf-8'))
            else:
                connection.send("You Lose!".encode('utf-8'))
        elif server_output == "scissors":
            if msg == "rock":
                connection.send("You Win!".encode('utf-8'))
            else:
                connection.send("You Lose!".encode('utf-8'))
    connection.send("Closing connection".encode('utf-8'))
    print("[Closing connection]")
    connection.close()


print("[Starting]")
server.listen()  # server listens for connections

while True:
    conn, addr = server.accept()  # accept request for connection, returns connection object and address of client
    print("Connection established. Address of client", addr)
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print("Number of active threads:", threading.activeCount()-1)
