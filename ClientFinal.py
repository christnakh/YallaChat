import socket
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading

chat_history = []
def signup(username, password):
    client.send(f"SIGNUP:{username}:{password}".encode())
    response = client.recv(1024).decode()
    messagebox.showinfo("Signup", response)

def login(username, password):
    client.send(f"LOGIN:{username}:{password}".encode())
    response = client.recv(1024).decode()
    if response == "Login successful":
        open_chat_page(username)
        root.destroy()
    else:
        messagebox.showerror("Login Error", response)

def open_chat_page(username):
    chat_window = tk.Toplevel()
    chat_window.title("Chat Page")
    
    frame = tk.Frame(chat_window)
    frame.pack(pady=10)
    
    online_friends_label = tk.Label(frame, text="Online Friends:")
    online_friends_label.grid(row=0, column=0, padx=5, pady=5)
    
    online_friends_listbox = tk.Listbox(frame, height=10, width=30)
    online_friends_listbox.grid(row=1, column=0, padx=5, pady=5)
    online_friends_listbox.bind("<Double-Button-1>", lambda event: open_chat(username, online_friends_listbox.get(tk.ACTIVE)))
    
    offline_friends_label = tk.Label(frame, text="Offline Friends:")
    offline_friends_label.grid(row=0, column=1, padx=5, pady=5)
    
    offline_friends_listbox = tk.Listbox(frame, height=10, width=30)
    offline_friends_listbox.grid(row=1, column=1, padx=5, pady=5)
    offline_friends_listbox.bind("<Double-Button-1>", lambda event: open_chat(username, offline_friends_listbox.get(tk.ACTIVE)))
    
    chats_label = tk.Label(frame, text="Chats:")
    chats_label.grid(row=2, column=0, padx=5, pady=5)
    
    chats_listbox = tk.Listbox(frame, height=15, width=60)
    chats_listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
    
    refresh_button = tk.Button(frame, text="Refresh", command=lambda: refresh(username, online_friends_listbox, offline_friends_listbox, chats_listbox))
    refresh_button.grid(row=4, column=0, padx=5, pady=5)
    
    add_friend_label = tk.Label(frame, text="Add Friend:")
    add_friend_label.grid(row=5, column=0, padx=5, pady=5)
    
    add_friend_entry = tk.Entry(frame)
    add_friend_entry.grid(row=5, column=1, padx=5, pady=5)
    
    add_friend_button = tk.Button(frame, text="Add", command=lambda: add_friend(username, add_friend_entry.get()))
    add_friend_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
    
    create_group_button = tk.Button(frame, text="Create Group", command=lambda: create_group(username, chats_listbox))
    create_group_button.grid(row=7, column=0, padx=5, pady=5)
    
    join_group_button = tk.Button(frame, text="Join Group", command=lambda: join_group(username, chats_listbox))
    join_group_button.grid(row=7, column=1, padx=5, pady=5)
    
    # New buttons for additional features
    notepad_button = tk.Button(frame, text="Notepad", command=Notepad)
    notepad_button.grid(row=8, column=0, padx=5, pady=5)
    
    task_list_button = tk.Button(frame, text="Task List", command=TaskList)
    task_list_button.grid(row=8, column=1, padx=5, pady=5)
    
    calculator_button = tk.Button(frame, text="Calculator", command=Calculator)
    calculator_button.grid(row=9, column=0, padx=5, pady=5)
    

    
    chat_window.mainloop()


def refresh(username, online_friends_listbox, offline_friends_listbox, chats_listbox):
    client.send(f"GET_FRIENDS:{username}".encode())
    response = client.recv(1024).decode()
    online_friends, offline_friends, joined_groups = response.split(";")
    online_friends_listbox.delete(0, tk.END)
    for friend in online_friends.split(","):
        online_friends_listbox.insert(tk.END, friend)
    offline_friends_listbox.delete(0, tk.END)
    for friend in offline_friends.split(","):
        offline_friends_listbox.insert(tk.END, friend)
    chats_listbox.delete(0, tk.END)
    for group in joined_groups.split(","):
        chats_listbox.insert(tk.END, f"Group: {group}")

def add_friend(username, friend_username):
    client.send(f"ADD_FRIEND:{username}:{friend_username}".encode())
    response = client.recv(1024).decode()
    messagebox.showinfo("Add Friend", response)

def create_group(username, chats_listbox):
    group_name = simpledialog.askstring("Create Group", "Enter group name:")
    if group_name:
        client.send(f"CREATE_GROUP:{username}:{group_name}".encode())
        response = client.recv(1024).decode()
        messagebox.showinfo("Create Group", response)
        if response == "Group created successfully":
            chats_listbox.insert(tk.END, f"Group: {group_name}")

def join_group(username, chats_listbox):
    group_name = simpledialog.askstring("Join Group", "Enter group name to join:")
    if group_name:
        client.send(f"JOIN_GROUP:{username}:{group_name}".encode())
        response = client.recv(1024).decode()
        messagebox.showinfo("Join Group", response)
        if response == "Joined group successfully":
            chats_listbox.insert(tk.END, f"Group: {group_name}")

def send_message(username, friend_username, message_entry):
    message = message_entry.get()
    if message:
        client.send(f"SEND_MESSAGE:{username}:{friend_username}:{message}".encode())
        message_entry.delete(0, tk.END)

def receive_message(username, chat_text, friend_username):
    while True:
        try:
            message = client.recv(1024).decode()
            if message.startswith("MESSAGE"):
                _, sender, msg = message.split(":", 2)
                if sender == friend_username:
                    chat_text.config(state=tk.NORMAL)
                    chat_text.insert(tk.END, f"{sender}: {msg}\n")
                    chat_text.config(state=tk.DISABLED)
                    chat_text.yview(tk.END)
                    chat_text.update()
        except Exception as e:
            print("Error receiving message:", e)
            break

def open_chat(username, friend_username):
    chat_window = tk.Toplevel()
    chat_window.title(f"Chat with {friend_username}")

    chat_frame = tk.Frame(chat_window)
    chat_frame.pack(padx=10, pady=10)

    chat_text = tk.Text(chat_frame, height=20, width=50)
    chat_text.config(state=tk.DISABLED)
    chat_text.pack(padx=10, pady=10)

    message_entry = tk.Entry(chat_frame, width=40)
    message_entry.pack(padx=10, pady=10)

    send_button = tk.Button(chat_frame, text="Send", command=lambda: send_message(username, friend_username, message_entry))
    send_button.pack(padx=10, pady=10)

    receive_thread = threading.Thread(target=receive_message, args=(username, chat_text, friend_username))
    receive_thread.start()

    # Check if there's chat history available for this chat
    if (username, friend_username) in chat_history:
        for entry in chat_history[(username, friend_username)]:
            # Ensure entry has the correct format before splitting
            if ":" in entry:
                sender, message = entry.split(":", 1)
                chat_text.config(state=tk.NORMAL)
                chat_text.insert(tk.END, f"{sender}: {message}\n")
                chat_text.config(state=tk.DISABLED)
                chat_text.yview(tk.END)
                chat_text.update()
            else:
                print("Invalid chat history entry:", entry)
    else:
        print("No chat history available for this chat.")
        

    client.send(f"GET_CHAT_HISTORY:{username}:{friend_username}".encode())


def start_client():
    global root, client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 9999))
    print("Connected to server.")

    root = tk.Tk()
    root.title("Chat Application")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    username_label = tk.Label(frame, text="Username:")
    username_label.grid(row=0, column=0, padx=5, pady=5)

    username_entry = tk.Entry(frame)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    password_label = tk.Label(frame, text="Password:")
    password_label.grid(row=1, column=0, padx=5, pady=5)

    password_entry = tk.Entry(frame, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    signup_button = tk.Button(frame, text="Signup", command=lambda: signup(username_entry.get(), password_entry.get()))
    signup_button.grid(row=2, column=0, padx=5, pady=5)

    login_button = tk.Button(frame, text="Login", command=lambda: login(username_entry.get(), password_entry.get()))
    login_button.grid(row=2, column=1, padx=5, pady=5)

    root.mainloop()

def Notepad():
    notepad_window = tk.Toplevel()
    notepad_window.title("Notepad")

    text = tk.Text(notepad_window, wrap=tk.WORD)
    text.pack(expand=1, fill=tk.BOTH)

    menu = tk.Menu(notepad_window)
    notepad_window.config(menu=menu)

    file_menu = tk.Menu(menu)
    menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Save", command=lambda: save_note(text))
    file_menu.add_command(label="Open", command=lambda: open_note(text))


def save_note(text_widget):
    note = text_widget.get(1.0, tk.END)
    with open("note.txt", "w") as file:
        file.write(note)
    messagebox.showinfo("Notepad", "Note saved successfully!")


def open_note(text_widget):
    try:
        with open("note.txt", "r") as file:
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.INSERT, file.read())
    except FileNotFoundError:
        messagebox.showerror("Notepad", "No saved notes found!")


def TaskList():
    task_list_window = tk.Toplevel()
    task_list_window.title("Task List")

    task_var = tk.StringVar()
    entry = tk.Entry(task_list_window, textvariable=task_var)
    entry.pack(pady=10)

    tasks = tk.Listbox(task_list_window)
    tasks.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    add_button = tk.Button(task_list_window, text="Add Task", command=lambda: add_task(task_var, tasks))
    add_button.pack(pady=10)

    remove_button = tk.Button(task_list_window, text="Remove Task", command=lambda: remove_task(tasks))
    remove_button.pack(pady=10)


def add_task(task_var, tasks_listbox):
    task = task_var.get()
    if task:
        tasks_listbox.insert(tk.END, task)
        task_var.set("")


def remove_task(tasks_listbox):
    try:
        index = tasks_listbox.curselection()[0]
        tasks_listbox.delete(index)
    except IndexError:
        pass


def Calculator():
    calculator_window = tk.Toplevel()
    calculator_window.title("Calculator")

    result_var = tk.StringVar()
    result_entry = tk.Entry(calculator_window, textvariable=result_var, font=("Arial", 24), bd=10, insertwidth=4,
                            width=14, justify='right')
    result_entry.grid(row=0, column=0, columnspan=4)

    buttons = [
        ('7', 1, 0), ('8', 1, 1), ('9', 1, 2),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
        ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('0', 4, 1),
        ('+', 1, 3), ('-', 2, 3), ('*', 3, 3), ('/', 4, 3),
        ('.', 4, 0), ('C', 4, 2), ('=', 5, 3)
    ]

    for (btn_text, row, col) in buttons:
        create_button(calculator_window, btn_text, row, col, result_var)


def create_button(window, text, row, col, result_var):
    btn = tk.Button(window, text=text, padx=20, pady=20, command=lambda: on_button_click(text, result_var))
    btn.grid(row=row, column=col)


def on_button_click(char, result_var):
    current_text = result_var.get()

    if char == 'C':
        result_var.set("")
    elif char == '=':
        try:
            result = eval(current_text)
            result_var.set(result)
        except Exception:
            result_var.set("Error")
    else:
        new_text = current_text + char
        result_var.set(new_text)



if __name__ == "__main__":
    start_client()
