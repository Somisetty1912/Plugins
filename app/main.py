from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import user

app = FastAPI(
    title="User API",
    description="API for user management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "User API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
