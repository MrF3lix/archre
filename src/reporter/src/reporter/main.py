import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from reporter.api.v1.endpoints import contract_diff, health
from reporter.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=settings.OPENAPI_URL,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # routers
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(contract_diff.router, prefix="/api/v1")

    return app


app = create_app()


def main():
    uvicorn.run(
        "reporter.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )


if __name__ == "__main__":
    main()
