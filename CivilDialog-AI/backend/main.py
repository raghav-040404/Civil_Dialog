from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.api.llm_routes import router as llm_router

app = FastAPI(
    title="CivilDialog AI Moderation Engine",
    description="LLM-powered real-time discussion moderation service for logical fallacy detection and respectful rewrites.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for integration with frontend / other services
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler for Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extract the error messages
    errors = exc.errors()
    error_msg = "Invalid request input."
    if errors:
        # Get the first error detail
        err = errors[0]
        field = ".".join([str(loc) for loc in err.get("loc", []) if loc != "body"])
        msg = err.get("msg", "Validation error")
        error_msg = f"{field}: {msg}" if field else msg

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": error_msg
        }
    )

# Exception Handler for standard HTTPExceptions
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )

# Exception Handler for all other unhandled internal server exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the actual exception locally (if a logger were set up)
    # Never expose internal stack trace or raw details to the user
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An unexpected internal server error occurred."
        }
    )

# Register route routers
app.include_router(llm_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the CivilDialog AI Moderation Engine API. Visit /docs for Swagger UI documentation."
    }
