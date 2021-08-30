#!/bin/bash
if [ ! -e .env ]
then
    cp .env.sample .env
    echo ".env copied"
fi

if [ "$1" = "run" ]
then
    COMPOSE_ARGS="$1 $2 --name opengenes-backend opengenes-backend"
    docker-compose $COMPOSE_ARGS

elif [ "$1" = "up" ]
then
    COMPOSE_ARGS="$1 $2"
    docker-compose $COMPOSE_ARGS
elif [ "$1" = "prod" ]
then
    pip3 install pipenv
    echo export PYTHONPATH=${PYTHONPATH}:${PWD} >> ${HOME}/.bashrc
    source ${HOME}/.bashrc
    pipenv install --deploy --system
fi



