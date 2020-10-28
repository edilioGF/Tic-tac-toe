import Tkinter as tk
import tkMessageBox
import socket
import threading

window_main = tk.Tk()
window_main.title("Tic Tac Toe")
top_frame = tk.Frame(window_main)

client = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 6020

list_labels = []
num_cols = 3
your_turn = False
you_started = False

your_details = {
    "name": "",
    "symbol": "X",
    "color" : "",
    "score" : 0
}

opponent_details = {
    "name": "",
    "symbol": "O",
    "color": "",
    "score": 0
}

for x in range(3):
    for y in range(3):
        lbl = tk.Label(top_frame, text=" ", font="Helvetica 40 bold", height=2, width=4, highlightbackground="grey",
                       highlightcolor="grey", highlightthickness=1, bg="white")
        lbl.bind("<Button-1>", lambda e, xy=[x, y]: get_cordinate(xy))
        lbl.grid(row=x, column=y)

        dict_labels = {"xy": [x, y], "symbol": "", "label": lbl, "ticked": False}
        list_labels.append(dict_labels)

top_frame.pack_forget()


def init(arg0, arg1):
    global list_labels, your_turn, your_details, opponent_details, you_started

    for i in range(len(list_labels)):
        list_labels[i]["symbol"] = ""
        list_labels[i]["ticked"] = False
        list_labels[i]["label"]["text"] = ""
        list_labels[i]["label"].config(foreground="black", highlightbackground="grey",
                                       highlightcolor="grey", highlightthickness=1)

    if you_started:
        you_started = False
        your_turn = False
    else:
        you_started = True
        your_turn = True


def get_cordinate(xy):
    global client, your_turn, you_started

    label_index = xy[0] * num_cols + xy[1]
    label = list_labels[label_index]

    if your_turn:
        if label["ticked"] is False:
            label["label"].config(foreground=your_details["color"])
            label["label"]["text"] = your_details["symbol"]
            label["ticked"] = True
            label["symbol"] = your_details["symbol"]
            client.send("$xy$" + str(xy[0]) + "$" + str(xy[1]))
            your_turn = False

            # Does this play leads to a win or a draw
            result = game_logic()
            if result[0] is True:
                if you_started:
                    message = opponent_details["symbol"] + " empieza la proxima ronda"
                else:
                    message = your_details["symbol"] + " empieza la proxima ronda"

            if result[0] is True and result[1] != "":
                your_details["score"] = your_details["score"] + 1
                tkMessageBox.showinfo(title="Ganaste!", message="Player " + your_details["symbol"] + ": " + str(your_details["score"]) + "       Player " + opponent_details["symbol"] + ": " + str(opponent_details["score"]) + '\n\n' + message )
                threading._start_new_thread(init, ("", ""))
            elif result[0] is True and result[1] == "":
                tkMessageBox.showinfo(title="Empate", message="Player " + your_details["symbol"] + ": " + str(your_details["score"])+ "       Player " + opponent_details["symbol"] + ": " + str(opponent_details["score"]) + '\n\n' + message )
                threading._start_new_thread(init, ("", ""))
    elif opponent_details['name'] == "":
        tkMessageBox.showinfo(title="Error", message="Esperando por el jugador 2")
    else:
        tkMessageBox.showinfo(title="Error", message="No es tu turno")


def check_row():
    list_symbols = []
    list_labels_temp = []
    winner = False
    win_symbol = ""
    for i in range(len(list_labels)):
        list_symbols.append(list_labels[i]["symbol"])
        list_labels_temp.append(list_labels[i])
        if (i + 1) % 3 == 0:
            if (list_symbols[0] == list_symbols[1] == list_symbols[2]):
                if list_symbols[0] != "":
                    winner = True
                    win_symbol = list_symbols[0]
            list_symbols = []
            list_labels_temp = []

    return [winner, win_symbol]

def check_col():
    winner = False
    win_symbol = ""
    for i in range(num_cols):
        if list_labels[i]["symbol"] == list_labels[i + num_cols]["symbol"] == list_labels[i + num_cols + num_cols][
            "symbol"]:
            if list_labels[i]["symbol"] != "":
                winner = True
                win_symbol = list_labels[i]["symbol"]

    return [winner, win_symbol]


def check_diagonal():
    winner = False
    win_symbol = ""
    i = 0
    j = 2

    a = list_labels[i]["symbol"]
    b = list_labels[i + (num_cols + 1)]["symbol"]
    c = list_labels[(num_cols + num_cols) + (i + 1)]["symbol"]
    if list_labels[i]["symbol"] == list_labels[i + (num_cols + 1)]["symbol"] == \
            list_labels[(num_cols + num_cols) + (i + 2)]["symbol"]:
        if list_labels[i]["symbol"] != "":
            winner = True
            win_symbol = list_labels[i]["symbol"]

    elif list_labels[j]["symbol"] == list_labels[j + (num_cols - 1)]["symbol"] == list_labels[j + (num_cols + 1)][
        "symbol"]:
        if list_labels[j]["symbol"] != "":
            winner = True
            win_symbol = list_labels[j]["symbol"]

    else:
        winner = False

    return [winner, win_symbol]

def check_draw():
    for i in range(len(list_labels)):
        if list_labels[i]["ticked"] is False:
            return [False, ""]
    return [True, ""]


def game_logic():
    result = check_row()
    if result[0]:
        return result

    result = check_col()
    if result[0]:
        return result

    result = check_diagonal()
    if result[0]:
        return result

    result = check_draw()
    return result

def connect_to_server():
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        
        # start a thread to keep receiving message from server
        threading._start_new_thread(receive_message_from_server, (client, "m"))
        top_frame.pack(side=tk.TOP)
        window_main.title("Tic-Tac-Toe " + your_details["name"])
    except Exception as e:
        tkMessageBox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(
            HOST_PORT) + " Server may be Unavailable. Try again later")


def receive_message_from_server(sck, m):
    global your_details, opponent_details, your_turn, you_started
    while True:
        from_server = sck.recv(4096)

        if not from_server: break

        if from_server.startswith("welcome"):
            if from_server == "welcome player 1":
                your_details["color"] = "blue"
                your_details["name"] = "player 1"
                opponent_details["color"] = "red"

            elif from_server == "welcome player 2":
                your_details["color"] = "red"
                your_details["name"] = "player 2"
                opponent_details["color"] = "blue"

        elif from_server.startswith("opponent_name$"):
            temp = from_server.replace("opponent_name$", "")
            temp = temp.replace("symbol", "")
            name_index = temp.find("$")
            symbol_index = temp.rfind("$")
            opponent_details["name"] = temp[0:name_index]
            your_details["symbol"] = temp[symbol_index:len(temp)]

            if your_details["symbol"] == "O":
                opponent_details["symbol"] = "X"
            else:
                opponent_details["symbol"] = "O"

            if your_details["symbol"] == "O":
                your_turn = True
                you_started = True
            else:
                you_started = False
                your_turn = False
        elif from_server.startswith("$xy$"):
            temp = from_server.replace("$xy$", "")
            _x = temp[0:temp.find("$")]
            _y = temp[temp.find("$") + 1:len(temp)]

            # update board
            label_index = int(_x) * num_cols + int(_y)
            label = list_labels[label_index]
            label["symbol"] = opponent_details["symbol"]
            label["label"]["text"] = opponent_details["symbol"]
            label["label"].config(foreground=opponent_details["color"])
            label["ticked"] = True

            result = game_logic()
            if result[0] is True:
                if you_started:
                    message = opponent_details["symbol"] + " empieza la proxima ronda"
                else:
                    message = your_details["symbol"] + " empieza la proxima ronda"

            if result[0] is True and result[1] != "":  # opponent win
                opponent_details["score"] = opponent_details["score"] + 1
                if result[1] == opponent_details["symbol"]:  #
                    tkMessageBox.showinfo(title="Perdiste", message="Player " + your_details["symbol"] + ": " + str(your_details["score"]) + "       Player " + opponent_details["symbol"] + ": " + str(opponent_details["score"]) + '\n\n' + message)
                    threading._start_new_thread(init, ("", ""))
            elif result[0] is True and result[1] == "":  # a draw
                tkMessageBox.showinfo(title="Empate", message="Player " + your_details["symbol"] + ": " + str(your_details["score"]) + "       Player " + opponent_details["symbol"] + ": " + str(opponent_details["score"]) + '\n\n' + message )
                threading._start_new_thread(init, ("", ""))
            else:
                your_turn = True

    sck.close()

connect_to_server()
window_main.mainloop()