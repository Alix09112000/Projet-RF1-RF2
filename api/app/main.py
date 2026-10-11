from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, health, imports, reference, users

app = FastAPI(
    title="Outil budget RF1/RF2 — Canalbox Côte d'Ivoire",
    version="0.2.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (health, auth, users, reference, imports):
    app.include_router(module.router, prefix="/api")
