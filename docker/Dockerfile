FROM alpine:3.21.3

# Set environment variables
ARG PROJ_NAME
ENV PROJ_NAME=${PROJ_NAME}

RUN mkdir -p /app/${PROJ_NAME}

# The following steps are executed from the specified directory below
WORKDIR /app/${PROJ_NAME}

# Install all necessary software
RUN apk add --no-cache python3 sqlite

# Create the directories, needed for persistent storage (e.g. database, tokens)
RUN mkdir ./data ./src ./config

# Create mount points for logs, data, src and config
VOLUME /var/log ./data ./src ./config

# Copy the application source code
COPY ./src/ ./src/

# Create a seperate venv inside the container & install requirements
COPY ./requirements.txt ./requirements.txt
RUN \
    python -m venv .venv && \
    source .venv/bin/activate && \
    ./.venv/bin/pip install -r ./requirements.txt && \
    deactivate

COPY ./docker/startup.sh ./startup.sh

# When starting the contianer the following is executed
ENTRYPOINT  ["./startup.sh"]
