"""
ETSY DASHBOARD API
Point d'entrée FastAPI principal
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.routers import auth, fees
from app.config import settings

# Initialisation FastAPI
app = FastAPI(
    title="Etsy Dashboard API",
    description="API privée pour Etsy Dashboard - Calculs financiers, analyses et recommandations IA",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # Swagger UI en dev seulement
    redoc_url="/redoc" if settings.DEBUG else None
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware pour logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    
    return response

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(fees.router, prefix="/api", tags=["Fees Calculator"])

# Health check
@app.get("/health")
async def health_check():
    """Endpoint de santé pour monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Etsy Dashboard API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler global pour les erreurs non gérées"""
    print(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
