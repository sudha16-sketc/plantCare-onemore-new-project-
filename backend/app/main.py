"""
Main FastAPI Application

This is the entry point for the Smart Plant Growth Assistant API.
It configures the FastAPI app, CORS, middleware, and includes all routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from app.services.plant import router as plant_router
from app.utils.config import settings



# Create FastAPI application instance
app = FastAPI(
    title="Smart Plant Growth Assistant API",
    description="""
    AI-powered backend for generating comprehensive plant care guidance.
    
    ## Features
    * 🌱 Generate detailed plant care guides using Gemini AI
    * 📊 Get growth stage information and timelines
    * 💡 Receive daily care routines and tips
    * 🐛 Learn about common problems and solutions
    * 📁 Generate visual guides (PPT/PDF) with NotebookLM
    
    ## How to Use
    1. Send plant information to `/generate-plant-guide`
    2. Receive comprehensive care guidance and visual assets
    3. Use the guidance to care for your plants successfully
    
    ## API Status
    Check `/health` endpoint for API status.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handle all uncaught exceptions globally.
    """
    debug = os.getenv("DEBUG", "False").lower() == "true"
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if debug else "An unexpected error occurred"
        }
    )

# Mount static files directory for generated PPT files
generated_files_dir = "generated_files"
os.makedirs(generated_files_dir, exist_ok=True)

try:
    app.mount("/files", StaticFiles(directory=generated_files_dir), name="files")
except Exception as e:
    print(f"Warning: Could not mount static files directory: {e}")

# Include routers
app.include_router(
    plant_router,
    tags=["Plant Care"]
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup.
    
    Perform any initialization tasks here.
    """
    import os
    print("=" * 80)
    print("🌱 PlantCare Backend - Smart Plant Growth Assistant API".center(80))
    print("=" * 80)
    print()
    print("  📍 Server Status:")
    print(f"     • Host: 0.0.0.0:8000")
    print(f"     • Environment: {'DEBUG' if os.getenv('DEBUG', 'False').lower() == 'true' else 'PRODUCTION'}")
    print()
    print("  🔐 API Security:")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    notebooklm_key = os.getenv("NOTEBOOKLM_API_KEY", "")
    print(f"     • Gemini API: {'✓ Configured' if gemini_key else '✗ Demo Mode (using mock data)'}")
    print(f"     • NotebookLM: {'✓ Configured' if notebooklm_key else '✗ Demo Mode (PPT generation enabled)'}")
    print()
    print("  📁 Generated Files:")
    os.makedirs("generated_files", exist_ok=True)
    print(f"     • Location: ./generated_files/")
    print(f"     • Access: http://localhost:8000/files/{{filename}}")
    print()
    print("  🌐 Frontend Integration:")
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    print(f"     • URLs: {cors_origins}")
    print()
    print("  📚 Documentation:")
    print("     • Swagger UI: http://localhost:8000/docs")
    print("     • ReDoc: http://localhost:8000/redoc")
    print("     • OpenAPI: http://localhost:8000/openapi.json")
    print()
    print("=" * 80)
    print()
    print("✨ API is ready! Send first request to /generate-plant-guide".center(80))
    print("=" * 80)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown.
    
    Perform cleanup tasks here.
    """
    print("=" * 60)
    print("🌱 Smart Plant Growth Assistant API Shutting Down...")
    print("=" * 60)


# Root endpoint (also available in routes, but good to have here)
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        Basic API information
    """
    return {
        "name": "Smart Plant Growth Assistant API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "health_check": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )