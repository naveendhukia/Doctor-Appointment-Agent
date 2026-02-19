from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import chat
from backend.app.models.schemas import HealthResponse

app = FastAPI(
    title="Doctor Appointment Agent API",
    description="AI-powered appointment scheduling system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="success",
        message="Doctor Appointment Agent API is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="success",
        message="API is healthy"
    )