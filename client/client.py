import socket
import threading
import curses

class ChatClient:
    def __init__(self, host='localhost', port=12345):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.messages = []
        self.running = True

    def receive_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    self.messages.append(message)
                    if len(self.messages) > 20:  # Limita o número de mensagens exibidas
                        self.messages.pop(0)  # Remove a mensagem mais antiga
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                self.running = False

    def send_messages(self, stdscr):
        input_win_y = curses.LINES - 1  # Linha da entrada
        input_buffer = ""  # Buffer para armazenar a entrada do usuário
        scroll_pos = 0  # Posição de rolagem da entrada

        while self.running:
            stdscr.clear()  # Limpa a tela a cada iteração

            # Exibe as mensagens recebidas
            for i, msg in enumerate(self.messages[-20:]):  # Exibe as últimas 20 mensagens
                stdscr.addstr(i, 0, msg)

            # Exibe o prompt para digitar a mensagem
            stdscr.addstr(input_win_y, 0, "Digite sua mensagem: ")
            display_buffer = input_buffer[scroll_pos:]  # Mostra apenas a parte do buffer visível
            
            # Adiciona indicadores de rolagem se necessário
            if scroll_pos > 0:
                display_buffer = "< " + display_buffer
            if len(input_buffer) - scroll_pos > curses.COLS - len("Digite sua mensagem: ") - 1:
                display_buffer += " >"

            # Ajusta a exibição para evitar erros de adição
            if len(display_buffer) <= curses.COLS - len("Digite sua mensagem: "):
                stdscr.addstr(input_win_y, len("Digite sua mensagem: "), display_buffer)  # Mostra a entrada atual
            else:
                # Ajusta o texto a ser mostrado na tela para evitar o erro
                stdscr.addstr(input_win_y, len("Digite sua mensagem: "), display_buffer[-(curses.COLS - len("Digite sua mensagem: ") - 1):])  # Limita a largura

            # Mova o cursor para a posição correta
            cursor_position = len("Digite sua mensagem: ") + len(display_buffer) - len(input_buffer) + scroll_pos
            stdscr.move(input_win_y, cursor_position)

            stdscr.refresh()  # Atualiza a tela antes de capturar a entrada

            # Captura a entrada do usuário
            key = stdscr.getch()  # Captura a tecla pressionada
            
            if key == curses.KEY_BACKSPACE or key == 127:  # Tratamento para backspace
                if input_buffer:  # Só remove se houver algo no buffer
                    input_buffer = input_buffer[:-1]  # Remove o último caractere
                    scroll_pos = max(0, scroll_pos - 1)  # Ajusta a posição de rolagem
            elif key in (curses.KEY_ENTER, 10, 13):  # Tratamento para o enter
                if input_buffer.startswith("/quit"):
                    self.running = False
                    self.client_socket.send(input_buffer.encode())
                elif input_buffer:  # Não envia se estiver vazio
                    self.client_socket.send(input_buffer.encode())  # Envia a mensagem ao servidor
                input_buffer = ""  # Limpa o buffer após enviar a mensagem
                scroll_pos = 0  # Reseta a posição de rolagem
            elif key == curses.KEY_LEFT:  # Tratamento para a tecla esquerda
                if scroll_pos > 0:
                    scroll_pos -= 1  # Move a posição de rolagem para a esquerda
            elif key == curses.KEY_RIGHT:  # Tratamento para a tecla direita
                if scroll_pos < len(input_buffer):
                    scroll_pos += 1  # Move a posição de rolagem para a direita
            elif key < 256:  # Apenas adiciona caracteres imprimíveis
                input_buffer += chr(key)  # Adiciona o caractere pressionado ao buffer
                scroll_pos = 0  # Reseta a posição de rolagem ao adicionar um novo caractere

    def start(self):
        # Inicia a thread para receber mensagens
        threading.Thread(target=self.receive_messages, daemon=True).start()
        # Inicializa a interface curses
        curses.wrapper(self.send_messages)

if __name__ == "__main__":
    client = ChatClient()
    client.start()
