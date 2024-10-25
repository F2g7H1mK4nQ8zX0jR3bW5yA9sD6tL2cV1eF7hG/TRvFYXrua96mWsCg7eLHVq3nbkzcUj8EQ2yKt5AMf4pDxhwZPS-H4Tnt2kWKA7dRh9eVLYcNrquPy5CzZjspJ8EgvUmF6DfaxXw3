import csv
import os

class UserManager:
    def __init__(self, filename='users.csv', blacklist_file='blacklist.csv', admin_file='admins.csv'):
        self.filename = filename
        self.blacklist_file = blacklist_file
        self.admin_file = admin_file
        self.load_users()
        self.load_blacklist()
        self.load_admins()

    def load_users(self):
        """ Carrega os usuários do arquivo CSV. """
        self.users = {}
        self.logged_in_users = {}  # Para controlar usuários logados
        if os.path.exists(self.filename):
            with open(self.filename, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 2:
                        username, password = row
                        self.users[username] = password

    def load_blacklist(self):
        """ Carrega a blacklist de IPs. """
        self.blacklist = set()
        if os.path.exists(self.blacklist_file):
            with open(self.blacklist_file, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:  # Verifica se a linha não está vazia
                        self.blacklist.add(row[0])  # Adiciona IP à blacklist

    def load_admins(self):
        """ Carrega os administradores do arquivo CSV. """
        self.admins = set()
        if os.path.exists(self.admin_file):
            with open(self.admin_file, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:  # Verifica se a linha não está vazia
                        self.admins.add(row[0])  # Adiciona admin à lista

    def register(self, username, password):
        """ Registra um novo usuário. Retorna True se o registro foi bem-sucedido. """
        if username in self.users:
            return False  # Usuário já existe
        self.users[username] = password
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, password])  # Salva o novo usuário
        return True

    def login(self, username, password, ip_address):
        """ Faz login de um usuário. Retorna True se o login foi bem-sucedido. """
        if ip_address in self.blacklist:
            return "Seu IP está bloqueado."  # IP bloqueado
        if username in self.logged_in_users:
            return "Erro: múltiplos usuários na mesma conta."  # Usuário já está logado
        if self.users.get(username) == password:
            self.logged_in_users[username] = ip_address  # Marca o usuário como logado
            return True
        return "Login falhou. Verifique suas credenciais."  # Credenciais inválidas

    def logout(self, username):
        """ Faz logout de um usuário. """
        if username in self.logged_in_users:
            del self.logged_in_users[username]

    def blacklist_ip(self, ip_address):
        """ Adiciona um IP à blacklist. """
        self.blacklist.add(ip_address)
        with open(self.blacklist_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([ip_address])  # Salva o IP na blacklist

    def remove_ip(self, ip_address):
        """ Remove um IP da blacklist. """
        if ip_address in self.blacklist:
            self.blacklist.remove(ip_address)
            self.save_blacklist()

    def save_blacklist(self):
        """ Salva a blacklist de IPs no arquivo. """
        with open(self.blacklist_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            for ip in self.blacklist:
                writer.writerow([ip])  # Salva cada IP da blacklist

    def is_admin(self, username):
        """ Verifica se o usuário é um administrador. """
        return username in self.admins

    def get_connected_users(self):
        """ Retorna a lista de usuários conectados. """
        return list(self.logged_in_users.keys())
