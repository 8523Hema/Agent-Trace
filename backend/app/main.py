import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    db_url = os.getenv("DATABASE_URL", "")
    if db_url.startswith("postgres://"):
        os.environ["DATABASE_URL"] = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        os.environ["DATABASE_URL"] = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base
from .routers import runs, steps, analyze

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"AgentTrace starting in {ENVIRONMENT} mode")
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs.router)
app.include_router(steps.router)
app.include_router(analyze.router)

@app.get("/")
async def root():
    return {"status": "ok"}
