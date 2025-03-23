# Predictify

## Overview

A Data analysis tool to scrape your Spotify History usage and let a ML-Model predict your next songs

## Authentication API

[Official Documentation](https://developer.spotify.com/documentation/web-api/tutorials/getting-started)
[Authorization Code Flow](https://developer.spotify.com/documentation/web-api/tutorials/code-flow)

## Usable possible APIs

Recently Played Tracks: `/me/player/recently-played` [Official Spotify Documentation](https://developer.spotify.com/documentation/web-api/reference/get-recently-played)

Get Track: `/tracks/{id}` [Official Spotify Documentation](https://developer.spotify.com/documentation/web-api/reference/get-track)

Get Track's Audio Features _(Deprecated)_: `/audio-features/{id}` [Official Spotify Documentation](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)

Get Track's Audio Analysis _(Deprecated)_: `/audio-analysis/{id}` [Official Spotify Documentation](https://developer.spotify.com/documentation/web-api/reference/get-audio-analysis)

Get Artist: `/artists/{id}` [Official Spotify Documentation](https://developer.spotify.com/documentation/web-api/reference/get-an-artist)

## Docker usage

`cd` inside the projects directory:
```sh
cd predictify
```
To run predictify inside a container, first make sure to build the image:
```sh
make dockerfile
```
Create a seperate data directory (e.g. `docker-data`):
```sh
mkdir docker-data
```
> [!NOTE]  
> To detatch the container to run it in the background add the `--detach` directly after the `run` command.
Then run the following docker command, to run the container in the foreground:
```sh
docker run \
    --name predictify \
    --network=host \
    --volume $(pwd)/data-docker:/app/predictify/data \
    --volume $(pwd)/config:/app/predictify/config \
    predictify:unstable
```

## GDPR Data

If you have gdpr data, create a folder: ```data/gdpr_data``` and add all .json files containing your play history into it. In order to extract it, run the script: ```python3 src/runtime.py --export```

## Authors

[Chris Kiriakou](https://github.com/ckiri)
[Dominik Agres](https://github.com/agresdominik)
