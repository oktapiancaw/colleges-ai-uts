from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware

from src.routes import alerts, preprocess, views
from src.core.db import MainSQL


def get_application() -> FastAPI:
    application = FastAPI(
        docs_url="/docs", title="Base Service", debug=False, version="0.0.1"
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(views.app, prefix="")
    application.include_router(alerts.app, prefix="/alerts")
    application.include_router(preprocess.app, prefix="/preprocess")

    @application.get("/rapidoc", response_class=HTMLResponse, include_in_schema=False)
    async def rapidoc():
        return f"""
            <!doctype html>
            <html>
                <head>
                    <meta charset="utf-8">
                    <script 
                        type="module" 
                        src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"
                    ></script>
                </head>
                <body>
                    <rapi-doc spec-url="{application.openapi_url}"></rapi-doc>
                </body> 
            </html>
        """

    return application


app = get_application()


@app.on_event("startup")
async def startup():
    app.state.baseDb = MainSQL()
