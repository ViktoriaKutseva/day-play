from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Get paths relative to this file
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Create FastAPI app
app = FastAPI(
    title="Day-Play Web",
    description="Gamified Task Management Web Interface",
    version="0.1.0"
)

# Setup static files serving
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render dashboard page."""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    """Render history page."""
    # For now, use dashboard template
    # TODO: Create history.html template
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    """Render settings page."""
    # For now, use dashboard template
    # TODO: Create settings.html template
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)