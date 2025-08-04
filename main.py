import traceback
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.controller import AuthController, UserController, ProductController
from app.database import engine
from app.models import models
from app.utils.ErrorModel import create_error_response

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API CRUD SENAC",
    description="API para operações CRUD",
    version="1.0.0"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for handling CORS
@app.middleware("http")
async def cors_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        # Log do erro
        print(f"Erro interno: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Retornar resposta com CORS habilitado
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
            }
        )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Gets the first error (can be modified to handle multiple errors)
    first_error = exc.errors()[0]
    field = first_error.get('loc', [None])[-1]
    message = first_error.get('msg', 'Erro de validação')
    code = "VALIDATION_ERROR"
    # Remove "Value error, " prefix if it exists
    if message.startswith("Value error, "):
        message = message.replace("Value error, ", "")
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            message=message,
            field=field,
            code=code
        )
    )


# Controllers
app.include_router(UserController.router, prefix="/api/v1/users", tags=["users"])
app.include_router(AuthController.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(ProductController.router)

@app.get("/")
def read_root():
    return {
        "message": "API CRUD SENAC está funcionando!",
        "documentation": "http://localhost:8000/docs",
        "alternative_docs": "http://localhost:8000/redoc",
        "endpoints": {
            "users": "/api/v1/users",
            "products": "/api/v1/products",
            "auth": "/api/v1/auth",
            "health": "/"
        }
    }