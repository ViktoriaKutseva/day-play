"""FastAPI application entry point for Day-Play API."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from day_play.config.logging_config import configure_logging
from day_play.config.settings import settings
from day_play.entrypoints.api.routes.dashboard import router as dashboard_router
from day_play.entrypoints.api.routes.gamification import router as gamification_router
from day_play.entrypoints.api.routes.history import router as history_router
from day_play.entrypoints.api.routes.tasks import router as tasks_router
from day_play.integrations.database.database import SessionLocal, init_db
from day_play.integrations.database.models import User
from day_play.models.exceptions import TaskNotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    configure_logging(log_level=settings.log_level)
    init_db()
    # Seed default user if not exists
    db = SessionLocal()
    try:
        if not db.get(User, 1):
            db.add(User(id=1, username="default_user", current_level=1, total_xp=0))
            db.commit()
    finally:
        db.close()
    yield
    # Shutdown (if needed)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Day-Play",
        version="0.1.0",
        description="Gamified daily task management application",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For MVP; restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup static files and templates for web interface
    web_dir = Path(__file__).resolve().parent.parent / "web"
    static_dir = web_dir / "static"
    templates_dir = web_dir / "templates"

    # Mount static files
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Setup Jinja2 templates
    templates = Jinja2Templates(directory=str(templates_dir))

    # Include API routers
    app.include_router(tasks_router)
    app.include_router(dashboard_router)
    app.include_router(gamification_router)
    app.include_router(history_router)

    # Error handlers
    @app.exception_handler(TaskNotFoundError)
    async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "healthy"}

    # Web interface routes (HTML pages)
    @app.get("/", response_class=HTMLResponse, tags=["web"])
    async def dashboard_page(request: Request):
        """Render dashboard page."""
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request}
        )

    @app.get("/tasks", response_class=HTMLResponse, tags=["web"])
    async def tasks_page(request: Request):
        """Render task management page."""
        return templates.TemplateResponse(
            "tasks.html",
            {"request": request}
        )

    @app.get("/history", response_class=HTMLResponse, tags=["web"])
    async def history_page(request: Request):
        """Render history page."""
        # TODO: Create history.html template
        return templates.TemplateResponse(
            "history.html",
            {"request": request}
        )

    @app.get("/settings", response_class=HTMLResponse, tags=["web"])
    async def settings_page(request: Request):
        """Render settings page."""
        # TODO: Create settings.html template
        return templates.TemplateResponse(
            "settings.html",
            {"request": request}
        )


    return app


# Create the app instance for uvicorn
app = create_app()
