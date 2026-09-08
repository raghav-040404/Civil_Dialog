from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.moderation import router as moderation_router
from app.utils.exceptions import AppException
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.admin import router as admin_router

app = FastAPI(
    title="CivilDialog API",
    description="Backend API for proactive AI-assisted civil communication",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred."
            }
        }
    )


@app.get("/health")
async def health_check():
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "CivilDialog Backend"
        }
    }

app.include_router(
    admin_router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    moderation_router,
    prefix="/api/v1/moderation",
    tags=["Moderation"]
)