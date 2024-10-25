import socket
import threading

class ChatClient:
    def __init__(self, host='localhost', port=12345):
        self.server_address = (host, port)
        self.username = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """ Conecta ao servidor. """
        self.client_socket.connect(self.server_address)
        print(self.client_socket.recv(1024).decode())  # Mensagem do servidor

        threading.Thread(target=self.receive_messages, daemon=True).start()  # Inicia thread para receber mensagens

        while True:
            message = input()  # Lê mensagem do usuário
            self.send_message(message)

    def receive_messages(self):
        """ Recebe mensagens do servidor. """
        while True:
            try:
                message = self.client_socket.recv(1024).decode()  # Recebe mensagem
                print(message)  # Exibe mensagem recebida
            except:
                print("Você foi desconectado do servidor.")
                break

    def send_message(self, message):
        """ Envia mensagem ao servidor. """
        self.client_socket.send(message.encode())  # Envia a mensagem

if __name__ == "__main__":
    client = ChatClient()
    client.connect()  # Conecta ao servidor
