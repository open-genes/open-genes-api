#!/bin/bash
COMPOSE_ARG="build"

if [ ! -e .env ]
then
    cp .env.sample .env
    echo ".env copied"
fi

if [ "$1" = "run" ]
then
COMPOSE_ARG="$1 $2 --name opengenes-backend opengenes-backend"
fi

docker-compose $COMPOSE_ARG
