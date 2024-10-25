import csv
import os

class MessageLogger:
    def __init__(self, log_file='messages.log'):
        self.log_file = log_file
        self.create_log_file()

    def create_log_file(self):
        """ Cria o arquivo de log se não existir. """
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w') as file:
                file.write("")

    def log_message(self, addr, message):
        """ Registra uma mensagem no arquivo de log. """
        with open(self.log_file, mode='a') as file:
            file.write(f"{addr}: {message}\n")  # Registra o endereço e a mensagem
