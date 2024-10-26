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
        self.clients = {}  # Usar um dicionário para armazenar clientes e seus nomes
        self.rate_limiters = {}
        self.message_logger = MessageLogger()
        self.user_manager = UserManager()  # Inicializa UserManager
        print("Servidor iniciado...")

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
                if not message:  # Se a mensagem estiver vazia, o cliente se desconectou
                    break
                print(f"Mensagem recebida do cliente {addr}: {message}")  # Debug

                # Processa o comando
                username = self.process_command(client_socket, message, username, addr)

            except ValueError as ve:
                client_socket.send(f"Erro: {str(ve)}".encode())  # Envia mensagem de erro
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")  # Exibe erro no console
                break

        self.cleanup_client(client_socket, username)  # Limpeza após desconexão

    def process_command(self, client_socket, message, username, addr):
        """ Processa os comandos enviados pelos clientes. """
        if message.startswith("/register"):
            self.handle_register(client_socket, message)
        elif message.startswith("/login"):
            return self.handle_login(client_socket, message, addr)  # Passa addr para a função
        elif message.startswith("/users"):
            self.handle_users(client_socket, username)
        elif message.startswith("/msg"):
            self.handle_private_message(client_socket, message, username)
        elif message.startswith("/help"):
            self.handle_help(client_socket)
        elif username:  # Verifica se o usuário está logado
            self.handle_chat_message(client_socket, message, username)

        return username  # Retorna o username atualizado

    # Métodos auxiliares para cada comando
    def handle_register(self, client_socket, message):
        parts = message.split()
        if len(parts) == 3:  # Verifica se há 3 partes
            _, user, password = parts
            if self.user_manager.register(user, password):
                client_socket.send("Registro bem-sucedido!".encode())
            else:
                client_socket.send("Usuário já existe!".encode())
        else:
            client_socket.send("Uso incorreto. Use: /register <username> <password>".encode())

    def handle_login(self, client_socket, message, addr):
        parts = message.split()
        if len(parts) == 3:  # Verifica se há 3 partes
            _, user, password = parts
            login_result = self.user_manager.login(user, password, addr[0])  # Passa o IP para o UserManager
            if login_result == True:
                self.clients[client_socket] = user  # Adiciona cliente à lista com seu nome
                self.rate_limiters[client_socket] = RateLimiter(max_requests=5, timeframe=10)
                client_socket.send("Login bem-sucedido!".encode())
                self.broadcast(f"{user} entrou no chat.", client_socket, user)  # Notifica a todos
                return user
            else:
                client_socket.send(login_result.encode())  # Mensagem de erro
        else:
            client_socket.send("Uso incorreto. Use: /login <username> <password>".encode())
        return None

    def handle_users(self, client_socket, username):
        if username:
            connected_users = ", ".join(self.clients.values())  # Lista de usuários conectados
            client_socket.send(f"Usuários conectados: {connected_users}".encode())
        else:
            client_socket.send("Você precisa estar logado para usar este comando.".encode())

    def handle_private_message(self, client_socket, message, username):
        parts = message.split()
        if len(parts) >= 3:  # Verifica se há pelo menos 3 partes
            target_user = parts[1]
            private_message = ' '.join(parts[2:])
            self.send_private_message(username, target_user, private_message, client_socket)
        else:
            client_socket.send("Uso incorreto. Use: /msg <username> <mensagem>".encode())

    def handle_help(self, client_socket):
        help_text = (
            "/register <username> <password> - Cria uma nova conta.\n"
            "/login <username> <password> - Faz login em sua conta.\n"
            "/users - Lista usuários conectados.\n"
            "/msg <username> <mensagem> - Envia uma mensagem privada.\n"
            "/quit - Sai do chat."
        )
        client_socket.send(help_text.encode())

    def handle_chat_message(self, client_socket, message, username):
        self.rate_limiters[client_socket].is_allowed()
        formatted_message = f"{username}: {message}"  # Formata a mensagem
        self.broadcast(formatted_message, client_socket, username)  # Envia para todos
        self.message_logger.log_message(username, formatted_message)  # Loga a mensagem

    def cleanup_client(self, client_socket, username):
        """ Limpa a conexão do cliente. """
        if username:
            del self.clients[client_socket]  # Remove cliente da lista
            self.broadcast(f"{username} saiu do chat.", client_socket, username)  # Notifica a todos
        client_socket.close()  # Fecha a conexão

    def send_private_message(self, sender, target_user, message, client_socket):
        """ Envia uma mensagem privada para um usuário específico. """
        target_socket = None
        for sock, user in self.clients.items():
            if user == target_user:
                target_socket = sock
                break

        if target_socket:
            target_socket.send(f"[Mensagem de {sender}]: {message}".encode())  # Envia a mensagem ao usuário alvo
            client_socket.send(f"[Para {target_user}]: {message}".encode())  # Confirma para o remetente
        else:
            client_socket.send("Usuário não encontrado.".encode())  # Informa se o usuário não foi encontrado

    def broadcast(self, message, client_socket, username):
        """ Envia a mensagem a todos os clientes conectados, exceto ao que a enviou. """
        for client in self.clients:
            if client != client_socket:  # Não envia para o próprio cliente
                try:
                    client.send(message.encode())  # Envia a mensagem
                except Exception as e:
                    print(f"Erro ao enviar mensagem para um cliente: {e}")

    def start(self):
        """ Inicia o servidor e aceita conexões. """
        while True:
            client_socket, addr = self.server_socket.accept()  # Aceita nova conexão
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()  # Cria nova thread para o cliente

if __name__ == "__main__":
    server = ChatServer()
    server.start()  # Inicia o servidor
