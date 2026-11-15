import time
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging, logger
from app.schemas.health import RootInfoResponse

settings = get_settings()
setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="MASTERY — Beyond Marks. Towards Mastery. AI-powered Student Performance Analytics, Academic Risk Prediction and Career Readiness Platform.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProcessTimeLoggingMiddleware:
    """Pure ASGI middleware for process time tracking and access logging."""
    def __init__(self, app=None, asgi_app=None):
        self.asgi_app = app if app is not None else asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.asgi_app(scope, receive, send)
            return

        start_time = time.perf_counter()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = (time.perf_counter() - start_time) * 1000.0
                headers = list(message.get("headers", []))
                headers.append((b"x-process-time-ms", f"{process_time:.2f}".encode("latin1")))
                message["headers"] = headers
                status_code = message.get("status", 200)
                logger.info(
                    "%s %s -> %s (%.2f ms)",
                    scope.get("method", "GET"),
                    scope.get("path", "/"),
                    status_code,
                    process_time,
                )
            await send(message)

        await self.asgi_app(scope, receive, send_wrapper)


app.add_middleware(ProcessTimeLoggingMiddleware)


# Centralized Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_type": "HTTPException",
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error_type": "ValidationError",
            "detail": exc.errors(),
            "status_code": 422,
            "path": request.url.path,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception at %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error_type": "InternalServerError",
            "detail": "An internal server error occurred. Please contact the administrator.",
            "status_code": 500,
            "path": request.url.path,
        },
    )


# Root information endpoint
@app.get("/", response_model=RootInfoResponse, tags=["General"])
def root_endpoint() -> RootInfoResponse:
    """Returns basic service identification and diagnostic endpoint paths."""
    return RootInfoResponse()


# Mount versioned API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
