import Tkinter as tk
import socket
import threading
import random

window = tk.Tk()
window.title("Tic Tac Toe")
window.geometry("300x100")

connectionFrame = tk.Frame(window)
lblIp = tk.Label(connectionFrame, text = "Address: 127.0.0.1")
lblIp.pack(side=tk.LEFT)

lblPort = tk.Label(connectionFrame, text = "Port:6020")
lblPort.pack(side=tk.LEFT)
connectionFrame.pack(side=tk.TOP, pady=(5, 0))

MessageFrame = tk.Frame(window)
lblLine = tk.Label(MessageFrame, text="Server started").pack()
MessageFrame.pack(side=tk.BOTTOM, pady=(5, 10))

server = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 6020
client_name = " "
clients = []
clients_names = []
player_data = []

def start_server():
    global server, HOST_ADDR, HOST_PORT

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)

    threading._start_new_thread(accept_clients, (server, " "))

def accept_clients(the_server, y):
    while True:
        if len(clients) < 2:
            client, addr = the_server.accept()
            clients.append(client)

            threading._start_new_thread(send_receive_client_message, (client, addr))

def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, player_data, player0, player1

    if len(clients) == 3:
        return
    if len(clients) == 1:
        client_connection.send("welcome player 1")
        client_name = "player 1"
    elif len(clients) == 2:
        client_connection.send("welcome player 2")
        client_name = "player 2"

    clients_names.append(client_name)

    if len(clients) == 2:
        symbols = ["O", "X"]
        clients[0].send("opponent_name$" + clients_names[1] + "symbol" + symbols[0])
        clients[1].send("opponent_name$" + clients_names[0] + "symbol" + symbols[1])


    while True:

        # get the player move
        data = client_connection.recv(4096)
        if not data: break

        # player x,y coordinate data. forward to the other player
        if data.startswith("$xy$"):
            if client_connection == clients[0]:
                clients[1].send(data)
            else:
                clients[0].send(data)

    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    client_connection.close()

def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx

start_server()
window.mainloop()
