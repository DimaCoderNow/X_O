import socket
import threading
import time
import tkinter as tk


def listening_messages():
    global whose_turn
    print(client)
    while True:
        server_message = client.recv(1024).decode()
        print(server_message)
        key_message, value_message = server_message.split(";")
        if key_message == "whose_turn":
            display_info(value_message)
            whose_turn = value_message
        if key_message == "mark_you":
            mark_field(int(value_message), "X")
        elif key_message == "mark_enemy":
            mark_field(int(value_message), "O")
        elif key_message == "drawn_game":
            display_info("Ничья!")
            clear_field()
            time.sleep(3)
            if value_message == "p1":
                client.send("new_game;1".encode())
        elif key_message == "winner":
            display_info("Ты победил!")
            clear_field()
            time.sleep(3)
            client.send("new_game;1".encode())
        elif key_message == "dead":
            display_info("Ты проиграл!")
            clear_field()
            time.sleep(3)
        elif key_message == "enemy_escaped":
            display_info("Враг убежал!")
            client.close()
            connect_to_host_game()
            clear_field()
        elif key_message == "close_client":
            client.close()
            exit()


def check_main_alive():
    # Проверка основного потока
    main_thread = threading.main_thread()
    while True:
        time.sleep(1)
        if not main_thread.is_alive():
            print("Main is dead!")
            try:
                print("Send command: close")
                client.send("close_client;0".encode())
            except Exception as e:
                print(e)
            break
        try:
            client.send("".encode())
        except Exception as e:
            print(e)
            connect_to_host_game()


def clear_field():
    global whose_turn
    whose_turn = ""
    time.sleep(1)
    for j in range(9):
        time.sleep(0.2)
        all_buttons[j].configure(text="")
    for char in "321 ":
        time.sleep(0.8)
        all_buttons[4].configure(text=char)


def send_move(button_number):
    if whose_turn == "Ваш ход":
        client.send(f'move;{button_number};'.encode())


def mark_field(button_number, player):
    print("mark field: ", button_number, player)
    all_buttons[button_number - 1].configure(text=player)


def display_info(info_txt):
    print("display_info", info_txt)
    move_info.configure(text=info_txt)


def connect_to_host_game():
    global client

    if not whose_turn:
        # client = socket.socket()
        host_game = entry.get()
        # client.connect((host_game, 12345))
        try:
            client.connect((host_game, 12345))
            display_info("Ждем противника")
            print("Connect to server")
            connect_button.configure(text="Подключено", state='active')
            threading.Thread(target=listening_messages).start()
            threading.Thread(target=check_main_alive).start()
        except Exception as e:
            display_info("Проверьте IP")
            print(f"Failed to connect: {e}")


def on_closing():
    root.destroy()
    try:
        client.send("close_client;0".encode())
        client.close()
        print("Client Close")
    finally:
        exit()


if __name__ == "__main__":
    client = socket.socket()

    root = tk.Tk()
    root.title("Крестики&Нолики")
    root.configure(background="#2B2B2B")
    root.geometry("700x700+550+250")
    root.resizable(True, True)
    root.minsize(400, 400)
    root.maxsize(800, 800)

    all_buttons = []
    whose_turn = ""

    for i in range(9):
        all_buttons.append(tk.Button(master=root,
                                     text="",
                                     font=("Arial", 160, "bold"),
                                     bg="#3C3F41",
                                     fg="#F6F6F6",
                                     width=60,
                                     height=60,
                                     command=lambda number=i + 1: send_move(number)))

    for i in range(3):
        root.grid_columnconfigure(i, minsize=100, weight=1)
        root.grid_rowconfigure(i + 1, minsize=100, weight=1)
    root.grid_rowconfigure(1, minsize=50, weight=1)

    button_index = 0
    for row in range(3):  # 0, 1, 2
        for col in range(3):  # 0, 1, 2
            all_buttons[button_index].grid(row=row + 1, column=col, padx=5, pady=5)
            button_index += 1

    entry = tk.Entry(root, width=20, font=("Arial", 16))
    entry.insert(0, socket.gethostbyname(socket.gethostname()))
    entry.grid(row=0, column=0, padx=20)
    move_info = tk.Label(master=root,
                         text="Введите IP Сервера",
                         font=("Arial", 18, "bold"),
                         bg="#2B2B2B",
                         fg="#CB7730",
                         pady=10)
    move_info.grid(row=0, column=1)

    connect_button = tk.Button(root, text="Подключиться", font=("Arial", 12), command=connect_to_host_game)
    connect_button.grid(row=0, column=2, padx=20)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()
