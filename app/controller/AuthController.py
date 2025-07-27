from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.controller.UserController import get_user_repository
from app.database import get_db
from app.models import UserLogin
from app.repositories.UserRepository import UserRepository

router = APIRouter()

@router.post("/login")
def login(user_credentials: UserLogin, repo: UserRepository = Depends(get_user_repository)):
    """Autenticar usuário"""
    user = repo.authenticate(user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    return {
        "message": "Login realizado com sucesso", 
        "user_id": user.id_user,
        "email": user.email,
        "nome": user.nome
    }