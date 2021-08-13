# open-genes-backend

## Init project

Firstly, you should have deployed MySQL,

then run: 

```
sh open-genes.sh
```

## Run container instance

```
docker-compose run -d --name opengenes-backend opengenes-backend
```

*or*

```
sh open-genes.sh run -d
```

*or*

```
sh open-genes.sh run
```

## Use scripts

```
docker exec -it opengenes-backend bash
python scripts/<your-script-path>
```

## Development

You can use Pipenv for local development. Just run:

```
pipenv install
```
