import sys
import asyncio
import logging
from contextlib import asynccontextmanager

if sys.platform == "win32":
    try:
        import uvicorn.loops.asyncio
        uvicorn.loops.asyncio.asyncio_loop_factory = lambda use_subprocess=False: asyncio.ProactorEventLoop
    except Exception:
        pass
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.database import init_db
from app.routes.health import router as health_router
from app.routes.scraper import router as scraper_router
from app.routes.portfolio import router as portfolio_router
from app.routes.analyzer import router as analyzer_router
from app.routes.export import router as export_router

# Setup structured logging
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger("optiinfo_scraper.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan Event Handler (Startup & Shutdown).
    """
    logger.info("Initializing database tables...")
    init_db()
    logger.info(f"{settings.PROJECT_NAME} started successfully.")
    yield
    logger.info(f"{settings.PROJECT_NAME} shutting down cleanly...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers (Never expose internal stack traces to client)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Input validation error at {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid input parameters", "errors": exc.errors()}
    )

@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database exception at {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again later."}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error at {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."}
    )

# Include Routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(scraper_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")
app.include_router(analyzer_router, prefix="/api")
app.include_router(export_router, prefix="/api")

# Also include under /api/v1 for backward compatibility
app.include_router(health_router, prefix="/api/v1")
app.include_router(scraper_router, prefix="/api/v1")
app.include_router(portfolio_router, prefix="/api/v1")
app.include_router(analyzer_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")
