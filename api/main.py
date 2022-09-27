from os import getenv
from typing import Optional

import uvicorn
from config import CONFIG, VERSION, Cache
from endpoints import (
    aging_mechanism,
    calorie_experiment,
    criteria,
    disease,
    functional_cluster,
    gene,
    phylum,
    protein_class,
    research,
    root,
)
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from pydantic import BaseModel


def assembling_endpoints(app: FastAPI):
    app.include_router(
        root.router,
        tags=["root"],
    )
    app.include_router(
        gene.router,
        tags=["gene"],
    )
    app.include_router(
        protein_class.router,
        tags=["protein_classes"],
    )
    app.include_router(
        phylum.router,
        tags=["phylum"],
    )
    app.include_router(
        disease.router,
        tags=["disease"],
    )
    app.include_router(
        calorie_experiment.router,
        tags=["calorie_experiment"],
    )
    app.include_router(
        aging_mechanism.router,
        tags=["aging_mechanism"],
    )
    app.include_router(
        functional_cluster.router,
        tags=["age_related_process"],
    )
    app.include_router(
        criteria.router,
        tags=["criteria"],
    )
    app.include_router(
        research.router,
        tags=["research"],
    )


origins = [
    "*",
]


def init():
    app = FastAPI(
        debug=CONFIG.get('DEBUG', False),
        title='Open Genes backend API',
        root_path=getenv('ROOT_PATH'),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    assembling_endpoints(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = init()


class Version(BaseModel):
    major: str
    minor: str
    build: Optional[str]
    date: Optional[str]
    revision: Optional[str]
    branch: Optional[str]


@app.get("/version", tags=["version"], summary="Version info", response_model=Version)
def version() -> dict:
    """
    Version information for the running application instance
    """
    return VERSION


@app.post("/clear_cache", tags=["cache"], summary="Clear cache")
async def clear(secret_token: str = Body(..., embed=True)):
    """Clears cache for all endpoints with given namespace. Secret token is required."""

    if secret_token == Cache.secret_token:
        await FastAPICache.clear(namespace=Cache.namespace)
        return {"status_code": 200, "detail": "Cache deleted successfully"}

    raise HTTPException(
        status_code=400,
        detail='Provided secret token is invalid',
    )


@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=str(VERSION.get('major', '0'))
        + '.'
        + str(VERSION.get('minor', '0'))
        + '.'
        + VERSION.get('build', '-'),
        routes=app.routes,
        servers=[{'url': CONFIG.get('API_URL', '')}],
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=CONFIG['API_HOST'],
        port=int(CONFIG['API_PORT']),
        reload=CONFIG.get('RELOAD', False),
        debug=CONFIG.get('DEBUG', False),  # debug=True implies reload=True
    )
