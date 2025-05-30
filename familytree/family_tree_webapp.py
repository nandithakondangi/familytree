import logging
import os
import sys

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

PYTHON_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PROJECT_DIR = os.path.dirname(PYTHON_DIR)
FRONTEND_DIST_DIR = os.path.join(BASE_PROJECT_DIR, "frontend", "dist")
INDEX_HTML_FILE = os.path.join(FRONTEND_DIST_DIR, "index.html")

sys.path.append(BASE_PROJECT_DIR)
sys.path.append(PYTHON_DIR)

from familytree.routers import chat_router, graph_router, manage_router  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FamilyTree API",
    version="1.0.0",
    description="API for the FamilyTree application, also serving the Vue.js frontend.",
)


@app.get("/api/v1", tags=["API Info"])
async def api_root():
    """Provides basic information about the API."""
    return {"message": "Welcome to the FamilyTree API v1", "version": app.version}


@app.get("/api/v1/health", tags=["Common"])
async def health_check():
    """A simple health check endpoint for the API."""
    return {"status": "ok", "message": "API is healthy"}


app.include_router(chat_router.router, prefix="/api/v1")
app.include_router(graph_router.router, prefix="/api/v1")
app.include_router(manage_router.router, prefix="/api/v1")


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_vue_frontend(full_path: str):
    """
    Serves static files from the Vue frontend build directory.
    If a file is not found, it serves the main index.html to allow
    client-side routing by the Vue application.

    Args:
        full_path: The path requested by the client.

    Returns:
        FileResponse: Either the requested static file or index.html.

    Raises:
        HTTPException: If an API path is mistakenly routed here or if index.html is not found.
    """
    if "api" in full_path.lower():
        logger.warning(
            f"API call requested: {full_path}. Either this is an invalid API path."
        )
        raise HTTPException(
            status_code=404,
            detail=f"API call requested: {full_path}. Either this is an invalid API path.",
        )

    static_file_path = os.path.join(FRONTEND_DIST_DIR, full_path)

    if os.path.isfile(static_file_path):
        return FileResponse(static_file_path)

    # If the requested path is not a direct file (e.g., for SPA routing like "/", "/about"),
    # or if the specific file doesn't exist, serve the main index.html.
    if os.path.exists(INDEX_HTML_FILE):
        return FileResponse(INDEX_HTML_FILE)

    logger.error(
        f"SPA index.html not found at {INDEX_HTML_FILE}. Ensure frontend is built. Requested path: {full_path}"
    )
    raise HTTPException(
        status_code=404, detail="SPA index.html not found. Ensure frontend is built."
    )
