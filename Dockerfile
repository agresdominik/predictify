FROM    alpine:latest

WORKDIR     /root

RUN         apk update && \
                apk add --no-cache \
                openssh \
                python3 \
                py3-pip \
                sqlite

EXPOSE      22

RUN         mkdir /root/src

COPY        ./startup.sh /root
COPY        ./requirements.txt /root
COPY        ./src/ /root/src/

RUN         ls -la

VOLUME      /root

ENTRYPOINT  ["/bin/sh", "/root/startup.sh"]
