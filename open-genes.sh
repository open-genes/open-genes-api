#!/bin/bash
if [ ! -e .env ]
then
    cp .env.sample .env
    echo ".env copied"
fi

[ -f VERSION ] || touch VERSION

if [ "$1" = "run" ]
then
    COMPOSE_ARGS="$1 $2 --name opengenes-backend opengenes-backend"
    docker-compose $COMPOSE_ARGS

elif [ "$1" = "up" ]
then
    COMPOSE_ARGS="$1 $2"
    docker-compose $COMPOSE_ARGS
elif [ "$1" = "dev" ]
then
    pdm install
fi



