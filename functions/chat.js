const socket = new WebSocket('ws://localhost:3000'); // URL do servidor WebSocket

socket.addEventListener('message', function(event) {
    addMessageToList(event.data); // Adiciona mensagem recebida ao chat
});

document.getElementById('chatForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Evita o envio do formulário

    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value;

    socket.send(message); // Envia a mensagem para o servidor
    messageInput.value = ''; // Limpa o campo de entrada
});

// Função para adicionar mensagem à lista
function addMessageToList(message) {
    const messagesList = document.getElementById('messages');
    const newMessageItem = document.createElement('li');
    newMessageItem.textContent = message;
    messagesList.appendChild(newMessageItem);
}
