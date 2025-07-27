from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controller import UserController
from app.database import engine
from app.models import models

# Criar as tabelas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API CRUD SENAC",
    description="API para operações CRUD",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(UserController.router, prefix="/api/v1/users", tags=["users"])

@app.get("/")
def read_root():
    return {
        "message": "API CRUD SENAC está funcionando!",
        "documentation": "http://localhost:8000/docs",
        "alternative_docs": "http://localhost:8000/redoc",
        "endpoints": {
            "users": "/api/v1/users",
            "health": "/"
        }
    }