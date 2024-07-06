import socket
import threading

# Store user credentials (username: password)
user_credentials = {}

# Store online users (username: socket)
online_users = {}

# Store friend relationships (username: set of friends)
friendships = {}

# Store group memberships (group_name: set of members)
group_memberships = {}

# Store group chats (group_name: list of messages)
group_chats = {}

# Store offline messages (username: list of (sender, message))
offline_messages = {}

chat_history = {}

def send_message(sender, receiver, message):
    if receiver in online_users:
        receiver_socket = online_users[receiver]
        receiver_socket.send(f"MESSAGE:{sender}:{message}".encode())
    else:
        offline_messages.setdefault(receiver, []).append((sender, message))

    chat_history.setdefault((sender, receiver), []).append((sender, message))

def retrieve_chat_history(sender, receiver):
    history = chat_history.get((sender, receiver), [])
    if not history:
        history = chat_history.get((receiver, sender), [])
    return history

def handle_client(client_socket, client_address):
    username = ""
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break

        print("Received from", client_address, ":", data)
        if data.startswith("SIGNUP"):
            _, new_username, password = data.split(":")
            if new_username not in user_credentials:
                user_credentials[new_username] = password
                client_socket.send("Signup successful".encode())
            else:
                client_socket.send("Username already exists".encode())
        elif data.startswith("LOGIN"):
            _, login_username, login_password = data.split(":")
            if login_username in user_credentials and user_credentials[login_username] == login_password:
                username = login_username
                online_users[username] = client_socket
                if username in offline_messages:
                    for sender, message in offline_messages[username]:
                        client_socket.send(f"MESSAGE:{sender}:{message}".encode())
                    del offline_messages[username]
                client_socket.send("Login successful".encode())
            else:
                client_socket.send("Invalid username or password".encode())
        elif data.startswith("GET_FRIENDS"):
            _, username = data.split(":")
            online_friends = ",".join([friend for friend in friendships.get(username, []) if friend in online_users])
            offline_friends = ",".join([friend for friend in friendships.get(username, []) if friend not in online_users])
            joined_groups = ",".join(group_chats.keys())
            client_socket.send(f"{online_friends};{offline_friends};{joined_groups}".encode())
        elif data.startswith("ADD_FRIEND"):
            _, username, friend_username = data.split(":")
            if friend_username in user_credentials and friend_username != username:
                friendships.setdefault(username, set()).add(friend_username)
                friendships.setdefault(friend_username, set()).add(username)
                client_socket.send("Friend added successfully".encode())
            else:
                client_socket.send("Friend does not exist".encode())
        elif data.startswith("CREATE_GROUP"):
            _, username, group_name = data.split(":")
            if group_name not in group_memberships:
                group_memberships[group_name] = set([username])
                client_socket.send("Group created successfully".encode())
            else:
                client_socket.send("Group name already exists".encode())
        elif data.startswith("JOIN_GROUP"):
            _, username, group_name = data.split(":")
            if group_name in group_memberships:
                group_memberships[group_name].add(username)
                client_socket.send("Joined group successfully".encode())
            else:
                client_socket.send("Group does not exist".encode())
        elif data.startswith("SEND_MESSAGE"):
            _, sender, receiver, message = data.split(":", 3)
            send_message(sender, receiver, message)
        elif data.startswith("GET_CHAT_HISTORY"):
            _, sender, receiver = data.split(":")
            history = retrieve_chat_history(sender, receiver)
            client_socket.send(f"CHAT_HISTORY:{';'.join([f'{sender}:{message}' for sender, message in history])}".encode())

    if username:
        del online_users[username]
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9999))
    server.listen(5)
    print("Server started. Listening on port 9999...")
    
    while True:
        client_socket, client_address = server.accept()
        print("Connection established with:", client_address)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
