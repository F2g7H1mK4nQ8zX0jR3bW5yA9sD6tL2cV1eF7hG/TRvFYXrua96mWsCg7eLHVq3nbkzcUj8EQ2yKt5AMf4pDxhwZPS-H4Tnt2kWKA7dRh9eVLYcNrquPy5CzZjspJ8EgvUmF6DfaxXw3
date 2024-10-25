# Use a imagem base do Alpine
FROM alpine:latest

# Instalação de dependências
RUN apk add --no-cache znc

# Criar diretório para a configuração do ZNC
RUN mkdir /znc && chown -R znc:znc /znc

# Copiar um arquivo de configuração padrão para o contêiner
COPY znc.conf /znc/znc.conf

# Alterar para o usuário não root
USER znc

# Expor a porta padrão do ZNC
EXPOSE 65001

# Comando para iniciar o ZNC
CMD ["znc", "-f", "-d", "/znc/znc.conf"]
