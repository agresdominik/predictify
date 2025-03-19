FROM    alpine:latest

WORKDIR /root

RUN     apk update && \
        apk add --no-cache \
            openssh \
            python3 \
            sqlite \
            pip \

EXPOSE      80
EXPOSE      22

VOLUME  /root/data
VOLUME  /root/app

ENTRYPOINT  /root/startup.sh;
