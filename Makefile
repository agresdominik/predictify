.PHONY: all dockerfile clean

TAG="unstable"
PROJ_NAME="predictify"

all: install dockerfile

install:
	mkdir -p ./data

dockerfile: ./docker/Dockerfile
	docker build \
		--tag "$(PROJ_NAME):$(TAG)" \
		--build-arg PROJ_NAME=$(PROJ_NAME) \
		--file ./docker/Dockerfile \
		.

clean: ./spotify_scraped.db
	rm -r ./data/spotify_scraped.db 
