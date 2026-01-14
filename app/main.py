from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.v1.routes import router as v1_router
from app.core.logging import get_logger

logger = get_logger()

app = FastAPI(
    title="SmartLoad Optimization API",
    description="Optimizes truck load selection for maximum payout",
    version="1.0.0"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with 400 Bad Request"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid input", "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors with 500 Internal Server Error"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

@app.middleware("http")
async def check_content_length(request: Request, call_next):
    """Reject requests with payload larger than 1MB with 413 Payload Too Large"""
    max_size = 1_000_000  # 1MB
    content_length = request.headers.get("content-length")
    
    if content_length and int(content_length) > max_size:
        logger.warning(f"Payload too large: {content_length} bytes")
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Payload too large. Maximum size is 1MB."}
        )
    
    return await call_next(request)

app.include_router(v1_router, prefix="/api/v1")
