import socket
import threading
from functions.rate_limit import RateLimiter
from functions.message_log import MessageLogger
from functions.user_management import UserManager

class ChatServer:
    def __init__(self, host='localhost', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        self.clients = []  # Lista para armazenar clientes conectados
        self.rate_limiters = {}
        self.message_logger = MessageLogger()
        self.user_manager = UserManager()  # Inicializa UserManager

    def handle_client(self, client_socket, addr):
        print(f'Nova conexão: {addr}')
        ip_address = addr[0]
        
        if ip_address in self.user_manager.blacklist:  # Verifica blacklist
            client_socket.send("Seu IP está bloqueado.".encode())
            client_socket.close()
            return

        username = None
        client_socket.send("Por favor, entre com suas credenciais usando /login <username> <password>".encode())

        while True:
            try:
                message = client_socket.recv(1024).decode()  # Recebe mensagem
                print(f"Mensagem recebida do cliente: {message}")  # Debug

                if message.startswith("/register"):
                    _, user, password = message.split()
                    if self.user_manager.register(user, password):
                        client_socket.send("Registro bem-sucedido!".encode())
                    else:
                        client_socket.send("Usuário já existe!".encode())
                elif message.startswith("/login"):
                    _, user, password = message.split()
                    login_result = self.user_manager.login(user, password, ip_address)
                    if login_result == True:
                        username = user
                        self.clients.append(client_socket)  # Adiciona cliente à lista
                        self.rate_limiters[client_socket] = RateLimiter(max_requests=5, timeframe=10)
                        client_socket.send("Login bem-sucedido!".encode())
                        self.broadcast(f"{username} entrou no chat.", client_socket)  # Notifica a todos
                    else:
                        client_socket.send(login_result.encode())  # Mensagem de erro
                elif message.startswith("/blacklist") and username and self.user_manager.is_admin(username):
                    _, target_ip = message.split()
                    self.user_manager.blacklist_ip(target_ip)
                    self.broadcast(f"{username} adicionou {target_ip} à blacklist.", client_socket)  # Notifica a todos
                elif message.startswith("/remove_ip") and username and self.user_manager.is_admin(username):
                    _, target_ip = message.split()
                    self.user_manager.remove_ip(target_ip)
                    self.broadcast(f"{username} removeu {target_ip} da blacklist.", client_socket)  # Notifica a todos
                elif message.startswith("/users") and username and self.user_manager.is_admin(username):
                    connected_users = self.user_manager.get_connected_users()
                    client_socket.send(f"Usuários conectados: {', '.join(connected_users)}".encode())
                elif username:  # Verifica se o usuário está logado
                    self.rate_limiters[client_socket].is_allowed()
                    self.broadcast(f"{username}: {message}", client_socket)  # Envia para todos
                    self.message_logger.log_message(addr, f"{username}: {message}")
            except ConnectionResetError:
                break  # Tratamento de desconexão

        if username:
            self.user_manager.logout(username)  # Faz logout do usuário
            self.clients.remove(client_socket)  # Remove cliente da lista
            self.broadcast(f"{username} saiu do chat.", client_socket)  # Notifica a todos
        client_socket.close()  # Fecha a conexão

    def broadcast(self, message, client_socket):
        """ Envia a mensagem a todos os clientes conectados, exceto ao que a enviou. """
        for client in self.clients:
            if client != client_socket:  # Não envia para o próprio cliente
                try:
                    client.send(message.encode())  # Envia a mensagem
                except Exception as e:
                    print(f"Erro ao enviar mensagem para um cliente: {e}")

    def start(self):
        """ Inicia o servidor e aceita conexões. """
        print('Servidor iniciado...')
        while True:
            client_socket, addr = self.server_socket.accept()  # Aceita nova conexão
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()  # Cria nova thread para o cliente

if __name__ == "__main__":
    server = ChatServer()
    server.start()  # Inicia o servidor
