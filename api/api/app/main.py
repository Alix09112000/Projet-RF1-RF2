from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, engine, health, imports, inputs, parameters, reference, users

app = FastAPI(
    title="Outil budget RF1/RF2 — Canalbox Côte d'Ivoire",
    version="0.3.0",
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

for module in (health, auth, users, reference, imports, inputs, parameters, engine):
    app.include_router(module.router, prefix="/api")
