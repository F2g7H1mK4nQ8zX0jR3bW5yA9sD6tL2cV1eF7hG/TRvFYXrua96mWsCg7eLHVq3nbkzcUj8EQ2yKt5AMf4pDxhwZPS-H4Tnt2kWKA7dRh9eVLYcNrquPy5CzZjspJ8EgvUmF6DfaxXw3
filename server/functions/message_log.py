import csv
import os

class MessageLogger:
    def __init__(self, log_file='messages.log'):
        self.log_file = log_file
        self.create_log_file()
        self.last_messages = {}  # Dicionário para armazenar a última mensagem de cada cliente

    def create_log_file(self):
        """ Cria o arquivo de log se não existir. """
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w') as file:
                file.write("")  # Cria um arquivo vazio

    def log_message(self, addr, message):
        """ Registra uma mensagem no arquivo de log e atualiza a última mensagem do cliente. """
        with open(self.log_file, mode='a') as file:
            file.write(f"{addr}: {message}\n")  # Registra o endereço e a mensagem
        self.last_messages[addr] = message  # Atualiza a última mensagem do cliente

    def get_last_message(self, client_socket):
        """ Retorna a última mensagem do cliente. """
        return self.last_messages.get(client_socket.getpeername(), None)  # Usa o endereço do cliente para buscar a última mensagem
