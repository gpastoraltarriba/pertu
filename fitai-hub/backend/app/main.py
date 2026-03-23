from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"🚀 {settings.APP_NAME} arrancando...")
    yield
    # Shutdown
    print("👋 Apagando servidor...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Fitness SaaS + AI Platform",
    lifespan=lifespan,
)

# CORS — permitir peticiones desde el frontend y la app móvil
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers — los iremos añadiendo aquí
from app.routers import auth
app.include_router(auth.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/health")
async def health():
    return {"status": "healthy"}