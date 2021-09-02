import uvicorn
from fastapi import FastAPI

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
        debug=True,
        title='Open Genes backend API',
    )
    assembling_endpoints(app)
    return app


app = init()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=CONFIG['API_HOST'],
        port=int(CONFIG['API_PORT']),
        reload=True,
        debug=True,
    )
