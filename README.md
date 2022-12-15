# Open Genes API

[![API CI](https://github.com/open-genes/open-genes-api/actions/workflows/api.yml/badge.svg?branch=master)](https://github.com/open-genes/open-genes-api/actions/workflows/api.yml)
[![CodeQL](https://github.com/open-genes/open-genes-api/actions/workflows/codeql-analysis.yml/badge.svg?branch=master)](https://github.com/open-genes/open-genes-api/actions/workflows/codeql-analysis.yml)

Open Genes API is based on [FastAPI](https://fastapi.tiangolo.com/) framework and provides data for genes and experiments in Open Genes database.

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

### Dependencies

All dependencies are listed in **./requirements_dev.txt**

### Linters

Please use linter and code auto formatting when contributing to this repository.

#### Configs: 
- .pylintrc
- pyproject.toml

