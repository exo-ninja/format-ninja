from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database components
from app.db.database import Base, engine

# Import models
from app.db.models import TransformationJob

app = FastAPI(
    title="Format Ninja", description="Data Transformation Service API", version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create database tables
def init_db():
    Base.metadata.create_all(bind=engine)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database tables created successfully")


# Simple root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Format Ninja API", "status": "online"}


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers here when you create them
# from app.routers import transform
# app.include_router(transform.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
