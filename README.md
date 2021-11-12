# open-genes-backend

## Architecture

- **api** - API application root
  - *main.py* - entry point
  - **endpoints** - api endpoints
  - **db** - domain access object (DAO) logic for DB
  - **entities** - domain entities

- **scripts** - maintenance scripts root
  - *aging_mechanisms* -
  - *clocks* - 
  - *icd* -
  - *translations* -
  - *uniprot* -

## Development

### Build local development image

```
./open-genes-backend.sh build
```

### Run API app in development mode

```
./open-genes-backend.sh run api
```

### Get the shell to run scripts

```
./open-genes-backend.sh run scripts
```
