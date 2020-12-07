import ast
import socket

# Dane potrzebne do połączenia się z serwerem
PORT = 65001
HOST = '127.0.0.1'
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
HEADER = 200
DISCONNECT_MESSAGE = "DISCONNECT"


class Client:
    """
    Client class for application.
    It handles connection to server, sending and getting messages.
    It sends requests as -> <REQUEST>:::.
    Which is afterwards smartly handled by server.
    """
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.available_civilizations = None
        self.current_players_on_server = None
        self.nick = None
        self.players = []


    # This method listens for messages from server.
    def rec_msg(self):
        msg_len = self.sock.recv(HEADER).decode(FORMAT)
        incoming_msg = ""
        if msg_len:
            incoming_msg = self.sock.recv(int(msg_len)).decode(FORMAT)
        return incoming_msg

    # This method sends requests on server and expects response.
    def send_msg(self, msg):
        message = msg.encode(FORMAT)
        message_length = len(message)
        send_length = str(message_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        self.sock.send(send_length)
        self.sock.send(message)
        # print("THE MESSAGE HAS BEEN SENT")
        # print(sock.recv(2048).decode(FORMAT))
        response = self.rec_msg()
        if response:
            # print("TU")
            print(response)
        return response

    # This method sends request and DOES NOT expect response.
    def only_send(self, msg):
        message = msg.encode(FORMAT)
        message_length = len(message)
        send_length = str(message_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        self.sock.send(send_length)
        self.sock.send(message)

    # Standard connection method
    def connect(self):
        self.sock.connect(ADDR)

    # Standard disconnection method
    def disconnect(self):
        self.send_msg(DISCONNECT_MESSAGE)
        self.sock.close()

    # Method allowing to send basic info to server
    def introduce_yourself(self, chosen_nick, chosen_civ):
        # TODO maybe only_send?
        self.nick = chosen_nick
        self.send_msg("ADD_NEW_PLAYER:" + chosen_nick + "::")
        self.send_msg("CHOOSE_CIVILISATION:" + chosen_nick + ":" + chosen_civ + ":")
        self.rec_msg()

    # Method sends request for available civilizations and gets response
    def get_available_civilizations_from_server(self):
        self.available_civilizations = self.send_msg("LIST_CIVILIZATIONS:::")
        return self.available_civilizations

    # Standard getter
    def get_available_civilizations(self):
        self.get_available_civilizations_from_server()
        return self.available_civilizations

    # Method sends request for current players and gets response
    def get_current_players_from_server(self):
        self.current_players_on_server = self.send_msg("LIST_PLAYERS:::")
        return self.current_players_on_server

    # Standard getter
    def get_current_players(self):
        self.get_current_players_from_server()
        return self.current_players_on_server

    # Standard setter
    def set_nickname(self, nick):
        self.nick = nick

    # Method gets map from server
    def get_map_from_server(self):
        map = self.send_msg("SHOW_MAP:::")
        return map

    # Method used only by server to inform all connected clients to begin exit lobby procedure
    def exit_lobby(self):
        self.only_send("EXIT_LOBBY:::")

    # Method used only by server to inform all connected clients to begin start game procedure
    def start_game(self):
        self.send_msg("START_GAME:::")

    # Widely used method by every client to inform about ending your turn
    def end_turn(self):
        self.send_msg("END_TURN:::")

    # This method is called when new player connects to server.
    # Difference between this method and get_current_players_from_server is
    # that this one only receives from server freshly connected player.
    def get_new_player(self):
        new_player = self.rec_msg()
        return new_player.split(":")

    def get_opponents_move(self):
        """
        Used while the player is waiting for their turn. Waits for a server message describing an action (turn end,
        unit moved, etc.) and parses it to a form that game_view is able to understand - a tuple of (ACTION, args...),
        for instance ("TURN", name of the player whose turn begins) or ("MOVE", x0, y0, x1, y1) when a unit is moved
        from (x0, y0) to (x1, y1).
        """
        mes = self.rec_msg()
        turn, name = ast.literal_eval(mes)
        return turn, name
