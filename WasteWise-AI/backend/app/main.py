
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Existing API routers
from app.api.v1 import (
    auth,
    batches,
    dashboard,
    products,
    recommendations,
    risk,
    sales,
    waste
)

# Authentication database
from app.auth.database import Base, engine
from app.auth import models
from app.auth.routes import router as authentication_router


# Create FastAPI application
app = FastAPI(
    title="WasteWise AI API",
    description="AI-powered inventory and food waste management system",
    version="1.0.0"
)


# Connect React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create authentication database tables
Base.metadata.create_all(bind=engine)


# Register existing API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(batches.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(risk.router, prefix="/api/v1")
app.include_router(sales.router, prefix="/api/v1")
app.include_router(waste.router, prefix="/api/v1")
app.include_router(authentication_router)

# Register new authentication router
app.include_router(authentication_router)


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to WasteWise AI API",
        "status": "running"
    }


# Health endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
