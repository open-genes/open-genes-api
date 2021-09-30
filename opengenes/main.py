import uvicorn
from os import getenv
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from opengenes.api import gene, disease
from opengenes.config import CONFIG


def assembling_endpoints(app: FastAPI):
    app.include_router(
        gene.router,
        prefix="/api",
        tags=["gene"],
    )
    app.include_router(
        disease.router,
        prefix="/api",
        tags=["disease"],
    )


def init():
    app = FastAPI(
        debug=CONFIG['DEBUG'],
        title='Open Genes backend API',
        root_path=getenv('ROOT_PATH')
    )
    assembling_endpoints(app)
    return app


app = init()

def custom_openapi():
    if app.openapi_schema: return app.openapi_schema
    openapi_schema = get_openapi(
        title="Open Genes backend API",
        version="0.1.0",
        routes=app.routes,
        servers=[{'url':'https://open-genes.com'}],
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=CONFIG['API_HOST'],
        port=int(CONFIG['API_PORT']),
        reload=True,
        debug=CONFIG['DEBUG'],
    )
