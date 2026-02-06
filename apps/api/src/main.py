from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import routes_chat, routes_datasets, routes_meta, routes_tasks
from middleware import AuthMiddleware, RateLimitMiddleware, RequestIDMiddleware
from observability.logging import configure_logging
from persistence.db import init_db
from settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
    init_db()

allowed_origins = settings.cors_origin_list()
if not allowed_origins and settings.app_env == "development":
    allowed_origins = ["*"]

allow_credentials = True
if allowed_origins == ["*"]:
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

app.include_router(routes_chat.router)
app.include_router(routes_tasks.router)
app.include_router(routes_meta.router)
app.include_router(routes_datasets.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin")
    headers = {}
    if origin:
        allowed = settings.cors_origin_list()
        if not allowed and settings.app_env == "development":
            headers["Access-Control-Allow-Origin"] = "*"
        elif origin in allowed:
            headers["Access-Control-Allow-Origin"] = origin
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": request.url.path,
        },
        headers=headers or None,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
