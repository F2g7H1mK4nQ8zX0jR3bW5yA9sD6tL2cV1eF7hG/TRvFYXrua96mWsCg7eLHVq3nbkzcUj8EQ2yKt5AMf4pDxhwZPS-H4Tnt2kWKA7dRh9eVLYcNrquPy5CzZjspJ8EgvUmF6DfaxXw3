FROM debian:latest

RUN apt-get update && apt-get install -y \
    tor \
    inspircd \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/lib/tor/irc_service && \
    chown -R tor:tor /var/lib/tor/irc_service

COPY torrc /etc/tor/torrc

EXPOSE 6667

CMD tor & inspircd