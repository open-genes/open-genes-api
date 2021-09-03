# open-genes-backend

## Architecture

- **opengenes** - root
  - *main.py* - entry point
  - **api** - api endpoints
  - **db** - domain access object (DAO) logic for DB
  - **entities** - domain entities

## Init production stand

```
sh open-genes.sh prod
```

## Init development stand

with virtual env

```
pipenv install
```

with local env

```
pipenv install --deploy --system
```

## Init containerized stand

### Up docker image

```
docker-compose up -d
```

*or*

```
sh open-genes.sh up -d
```

### Run docker container instance

```
docker-compose run -d --name opengenes-backend opengenes-backend
```

*or*

```
sh open-genes.sh run -d
```

### Use scripts in docker container

```
docker exec -it opengenes-backend bash
python scripts/<your-script-path>
```
