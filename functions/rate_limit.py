import time

class RateLimiter:
    def __init__(self, max_requests, timeframe):
        self.max_requests = max_requests  # Número máximo de requisições
        self.timeframe = timeframe  # Tempo em segundos
        self.requests = []  # Armazena timestamps das requisições

    def is_allowed(self):
        """ Verifica se a requisição é permitida. """
        current_time = time.time()  # Tempo atual
        # Remove requisições que estão fora do timeframe
        self.requests = [req for req in self.requests if req > current_time - self.timeframe]
        
        if len(self.requests) < self.max_requests:  # Se ainda há espaço
            self.requests.append(current_time)  # Adiciona requisição
            return True
        else:
            raise Exception("Você está enviando mensagens muito rapidamente.")  # Exceção para limite excedido
