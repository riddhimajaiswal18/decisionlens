"""FastAPI application entry point."""

import logging
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.router import api_router
from backend.app.config.settings import get_settings
from backend.app.ingestion.engine.exceptions import IngestionEngineError
from backend.app.intelligence.exceptions import IntelligenceError
from backend.app.memory.supermemory.exceptions import SupermemoryError

settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="HTTP API for DecisionLens ingestion and engineering-intelligence services.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def error_middleware(request: Request, call_next):
    """Translate existing service-layer errors into stable HTTP responses."""
    try:
        return await call_next(request)
    except IngestionEngineError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc), "code": exc.code})
    except IntelligenceError as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc), "code": "intelligence_error"})
    except SupermemoryError as exc:
        return JSONResponse(status_code=502, content={"detail": str(exc), "code": "memory_service_error"})
    except Exception:
        logger.exception("Unhandled request error", extra={"path": request.url.path})
        return JSONResponse(status_code=500, content={"detail": "Internal server error", "code": "internal_error"})


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log request completion without adding endpoint behavior."""
    started_at = perf_counter()
    response = await call_next(request)
    logger.info(
        "HTTP request completed",
        extra={"method": request.method, "path": request.url.path, "status_code": response.status_code, "duration_ms": round((perf_counter() - started_at) * 1000, 2)},
    )
    return response

app.include_router(api_router, prefix=settings.api_v1_prefix)
