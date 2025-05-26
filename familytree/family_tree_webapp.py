import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

# --- Configuration ---
PYTHON_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PROJECT_DIR = os.path.dirname(PYTHON_DIR)
FRONTEND_DIST_DIR = os.path.join(BASE_PROJECT_DIR, "frontend", "dist")
INDEX_HTML_FILE = os.path.join(FRONTEND_DIST_DIR, "index.html")

# --- Logger Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title="FamilyTree API",
    version="1.0.0",
    description="API for the FamilyTree application, also serving the Vue.js frontend.",
)


# --- API Endpoints ---
@app.get("/api/v1", tags=["API Info"])
async def api_root():
    """Provides basic information about the API."""
    return {"message": "Welcome to the FamilyTree API v1", "version": app.version}


@app.get("/api/v1/health", tags=["Common"])
async def health_check():
    """A simple health check endpoint for the API."""
    return {"status": "ok", "message": "API is healthy"}


@app.get("/api/v1/manage", tags=["Family Data"])
async def get_manage_data():
    """Placeholder for an endpoint to manage family data."""
    # Replace with your actual data fetching logic
    return {"message": "Data from /api/v1/manage", "items": ["item1", "item2"]}


@app.post("/api/v1/chat", tags=["Communication"])
async def post_chat_message(payload: dict):  # Assuming a JSON payload
    """Placeholder for a chat endpoint."""
    # Replace with your actual chat logic
    if not payload or "message" not in payload:
        raise HTTPException(
            status_code=400, detail="Payload must contain a 'message' field."
        )
    return {
        "status": "success",
        "received_message": payload.get("message"),
        "reply": "Message processed.",
    }


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_vue_frontend(full_path: str):
    """
    Serves static files from the Vue frontend build directory.
    If a file is not found, it serves the main index.html to allow
    client-side routing by the Vue application.
    """
    # Check if the path looks like an API call.
    if "api" in full_path.lower():
        logger.warning(
            f"API call requested: {full_path}. Either this is an invalid API path or it is not implemented yet."
        )
        raise HTTPException(
            status_code=404,
            detail=f"API call requested: {full_path}. Either this is an invalid API path or it is not implemented yet.",
        )

    # Construct the potential path to a static file
    static_file_path = os.path.join(FRONTEND_DIST_DIR, full_path)

    # Check if the requested path is a file and exists
    if os.path.isfile(static_file_path):
        return FileResponse(static_file_path)

    # If it's not a direct file (e.g., it's "/", "/about", "/user/profile", etc.),
    # or if the file doesn't exist, serve the main index.html for the SPA.
    if os.path.exists(INDEX_HTML_FILE):
        return FileResponse(INDEX_HTML_FILE)

    # If index.html itself is not found (which means frontend isn't built or path is wrong)
    logger.error(
        f"SPA index.html not found. Ensure frontend is built. Requested path: {full_path}"
    )
    raise HTTPException(
        status_code=404, detail="SPA index.html not found. Ensure frontend is built."
    )
