import logging
import os
import sys

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from google.protobuf.json_format import ParseError

PYTHON_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PROJECT_DIR = os.path.dirname(PYTHON_DIR)
FRONTEND_DIST_DIR = os.path.join(BASE_PROJECT_DIR, "frontend", "dist")
INDEX_HTML_FILE = os.path.join(FRONTEND_DIST_DIR, "index.html")

sys.path.append(BASE_PROJECT_DIR)
sys.path.append(PYTHON_DIR)

from familytree.exceptions import FamilyTreeBaseError  # noqa: E402
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


@app.exception_handler(FamilyTreeBaseError)
async def handle_custom_family_tree_errors(request: Request, exc: FamilyTreeBaseError):
    """
    Handles all errors that inherit from FamilyTreeBaseError.
    The context (operation, specific details) is part of the exception itself.
    """
    log_message = f"Custom App Error: {exc.__class__.__name__} during {exc.operation or 'unknown operation'} for {request.url.path}. Detail: {exc.detail}"
    logger.error(log_message, exc_info=True)  # exc_info=True adds traceback

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,  # The pre-formatted, context-aware message from the exception
            "operation": exc.operation,  # Optionally include more structured context
            # Add other relevant fields from your custom exception if needed
        },
    )


@app.exception_handler(ParseError)
async def handle_parse_errors(request: Request, exc: ParseError):
    """
    Handles protobuf ParseError, making the message slightly more user-friendly.
    """
    # Try to get operation name if available (e.g., from request.state if set by middleware, see below)
    operation_context = getattr(request.state, "operation_name", "request processing")
    error_message = f"Failed to parse request data for '{operation_context}'. Please ensure the data is in the correct format."
    logger.error(
        f"ParseError for {request.url.path} (Context: {operation_context}): {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=400,  # Bad Request
        content={"detail": error_message},
    )


@app.exception_handler(Exception)
async def handle_generic_exception(request: Request, exc: Exception):
    """
    Handles any other unhandled exceptions.
    """
    # Avoid re-handling HTTPExceptions that might be raised intentionally elsewhere
    # and are already handled by FastAPI's default mechanisms.
    if isinstance(exc, HTTPException):
        logger.warning(
            f"HTTPException caught by generic handler: {exc.status_code} - {exc.detail} for {request.url.path}"
        )
        raise exc

    operation_context = getattr(request.state, "operation_name", "an unknown operation")
    error_message = (
        f"An unexpected internal server error occurred during '{operation_context}'."
    )
    logger.critical(
        f"Unhandled generic exception during {operation_context} for {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": error_message},
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
app.add_exception_handler(FamilyTreeBaseError, handle_custom_family_tree_errors)
app.add_exception_handler(ParseError, handle_parse_errors)
app.add_exception_handler(Exception, handle_generic_exception)


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
