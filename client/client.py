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
        cursor_position = 0  # Posição do cursor na entrada

        while self.running:
            stdscr.clear()  # Limpa a tela a cada iteração

            # Exibe as mensagens recebidas
            for i, msg in enumerate(self.messages[-20:]):  # Exibe as últimas 20 mensagens
                stdscr.addstr(i, 0, msg)

            # Exibe o prompt para digitar a mensagem
            stdscr.addstr(input_win_y, 0, "Digite sua mensagem: ")

            # Limita o comprimento da entrada a não exceder a largura da tela
            max_input_length = curses.COLS - len("Digite sua mensagem: ") - 1
            display_input = input_buffer if len(input_buffer) <= max_input_length else input_buffer[-max_input_length:]

            # Adiciona os indicadores se a entrada estiver próxima do limite
            if len(input_buffer) > max_input_length - 2:  # Usa -2 para evitar erro
                display_input = display_input + " >"  # Adiciona o indicador '>'
                cursor_position = max_input_length  # Mantém o cursor no final visível
            else:
                cursor_position = len(display_input)  # Atualiza a posição do cursor normalmente

            # Evita adicionar uma string que exceda a largura da tela
            stdscr.addstr(input_win_y, len("Digite sua mensagem: "), display_input[:max_input_length])  # Mostra a entrada atual

            # Mova o cursor para a posição correta na linha de entrada
            stdscr.move(input_win_y, len("Digite sua mensagem: ") + cursor_position)

            stdscr.refresh()  # Atualiza a tela

            # Captura a entrada do usuário
            key = stdscr.getch()  # Captura a tecla pressionada

            if key == curses.KEY_BACKSPACE or key == 127:  # Tratamento para backspace
                if input_buffer:  # Só remove se houver algo no buffer
                    input_buffer = input_buffer[:-1]  # Remove o último caractere
                    cursor_position = max(0, cursor_position - 1)  # Ajusta a posição do cursor
            elif key in (curses.KEY_ENTER, 10, 13):  # Tratamento para o enter
                if input_buffer.startswith("/quit"):
                    self.running = False
                    self.client_socket.send(input_buffer.encode())
                elif input_buffer:  # Não envia se estiver vazio
                    self.client_socket.send(input_buffer.encode())  # Envia a mensagem ao servidor
                input_buffer = ""  # Limpa o buffer após enviar a mensagem
                cursor_position = 0  # Reseta a posição do cursor
            elif key == curses.KEY_LEFT:  # Tratamento para a tecla esquerda
                if cursor_position > 0:
                    cursor_position -= 1  # Move o cursor para a esquerda
            elif key == curses.KEY_RIGHT:  # Tratamento para a tecla direita
                if cursor_position < len(input_buffer):
                    cursor_position += 1  # Move o cursor para a direita
            elif key < 256:  # Apenas adiciona caracteres imprimíveis
                input_buffer = input_buffer[:cursor_position] + chr(key) + input_buffer[cursor_position:]  # Insere o caractere no cursor
                cursor_position += 1  # Move o cursor para a direita
                if cursor_position > max_input_length:  # Limita o cursor
                    cursor_position = max_input_length

    def start(self):
        # Inicia a thread para receber mensagens
        threading.Thread(target=self.receive_messages, daemon=True).start()
        # Inicializa a interface curses
        curses.wrapper(self.send_messages)

if __name__ == "__main__":
    client = ChatClient()
    client.start()
