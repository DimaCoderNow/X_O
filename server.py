import random
import socket
import threading


def main_game(p1, p2):
    print("main start")
    step = 0
    whose_turn = random.choice((p1, p2))
    winner_lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (6, 4, 2)]
    game_field = []

    def new_game():
        nonlocal step
        nonlocal game_field
        print("Start new game")
        step = 0
        game_field = ["" for i in range(9)]
        send_whose_turn()

    #  Прием команд от игрока
    def receiving_command(player):
        nonlocal whose_turn
        while True:
            try:
                player_message = player.recv(1024).decode()
            except Exception as e:
                print(e)
                break
            print(player_message)
            if not player_message:
                print("Пустая команда")
                break
            command = player_message.split(";")[0]
            button_number = int(player_message.split(";")[1])
            if command == "move":
                button_cliks(button_number)
                print(button_number)
            elif command == "close_client":
                if player == p1:
                    p2.send("enemy_escaped;0".encode())
                    p1.send("close_client;0".encode())
                else:
                    p1.send("winner;0".encode())
                    p2.send("enemy_escaped;0".encode())
                break
            elif command == "new_game":
                new_game()

    #  Отправка в инфо информацию о том чей ход
    def send_whose_turn():
        if whose_turn == p1:
            print("Ход p1")
            p1.send("whose_turn;Ваш ход".encode())
            p2.send("whose_turn;Ход противника".encode())
        else:
            print("Ход p2")
            p2.send("whose_turn;Ваш ход".encode())
            p1.send("whose_turn;Ход противника".encode())

    def send_mark(button_number):
        if whose_turn == p1:
            p1.send(f"mark_you;{button_number}".encode())
            p2.send(f"mark_enemy;{button_number}".encode())
        else:
            p2.send(f"mark_you;{button_number}".encode())
            p1.send(f"mark_enemy;{button_number}".encode())

    def button_cliks(button_number):
        nonlocal game_field
        nonlocal step
        nonlocal whose_turn

        print(whose_turn)
        if step < 9:
            if game_field[button_number - 1] != "":
                print("Поле занято")
                return
            print("Поле свободно")
            game_field[button_number - 1] = whose_turn

            if check_winner():
                print("Победил", whose_turn)
                send_mark(button_number)
                if whose_turn == p1:
                    p1.send("winner;".encode())
                    p2.send("dead;".encode())
                else:
                    p2.send("winner;".encode())
                    p1.send("dead;".encode())
                return
            if step >= 9:
                send_mark(button_number)
                p1.send("drawn_game;p1".encode())
                p2.send("drawn_game;".encode())
                return

            # Обновляем инфо у клиентов
            send_mark(button_number)
            if whose_turn == p1:
                whose_turn = p2
            else:
                whose_turn = p1
            send_whose_turn()

    def check_winner():
        nonlocal step
        nonlocal whose_turn
        for i, (a, b, c) in enumerate(winner_lines):
            if whose_turn == game_field[a] == game_field[b] == game_field[c]:
                step = 9
                return True

        step += 1
        return False

    threading.Thread(target=receiving_command, args=(p1,)).start()
    threading.Thread(target=receiving_command, args=(p2,)).start()
    new_game()
    print("main finish")


if __name__ == "__main__":
    server = socket.socket()
    hostname = socket.gethostname()
    server.bind((hostname, 12345))
    server.listen(2)
    print("server is running and listening")
    print(f"IP сервера {server.getsockname()[0]}")

    new_player_1 = None
    new_player_2 = None

    while True:
        connection, address = server.accept()
        print("connection:", connection)
        print("address:", address)

        if not new_player_1:
            new_player_1 = connection
            print("Player_1 connected!")
        else:
            new_player_2 = connection
            print("Player_2 connected!")
        #  Если игроки подключены, запускаем поток с игрой
        if new_player_2 and new_player_1:
            threading.Thread(target=main_game, args=(new_player_1, new_player_2)).start()
            new_player_1 = None
            new_player_2 = None

        # connection.close()
