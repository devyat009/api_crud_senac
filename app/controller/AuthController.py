from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.controller.UserController import get_user_repository
from app.database import get_db
from app.models import UserLogin
from app.repositories.UserRepository import UserRepository
from app.utils.ErrorModel import create_error_response

router = APIRouter()

@router.post("/login")
def login(user_credentials: UserLogin, repo: UserRepository = Depends(get_user_repository)):
    """User login endpoint"""
    try:
        user = repo.authenticate(user_credentials.email, user_credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_error_response(
                    message="Email ou senha incorretos",
                    field="credentials",
                    code="INVALID_CREDENTIALS"
                )
            )
        
        return {
            "success": True,
            "message": "Login realizado com sucesso", 
            "user_id": user.id_user,
            "email": user.email,
            "nome": user.nome,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                message="Erro interno do servidor",
                code="INTERNAL_SERVER_ERROR"
            )
        )