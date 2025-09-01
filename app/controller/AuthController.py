from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.controller.UserController import get_user_repository
from app.database import get_db
from app.models import *
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
            "role": user.role
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
        
@router.post("/forgot-password")
def confirm_data_forgot_password(
    data: UserForgotPasswordRequest,
    repo: UserRepository = Depends(get_user_repository)
):
    """Confirm data for password recovery"""
    user = repo.confirm_forgot_password_data(data.email, data.cpf, data.data_nascimento)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                message="Dados não conferem com nenhum usuário",
                field=None,
                code="USER_NOT_FOUND"
            )
        )
    return {
        "success": True,
        "message": "Dados conferem. Pode alterar a senha.",
        "user_id": user.id_user
    }

@router.put("/change-password")
def change_password(
    data: UserChangePasswordRequest,
    repo: UserRepository = Depends(get_user_repository)
):
    """Change user password"""
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                message="Senhas não coincidem",
                field="confirm_password",
                code="PASSWORD_MISMATCH"
            )
        )
    success = repo.change_password(data.user_id, data.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                message="Usuário não encontrado",
                field="user_id",
                code="USER_NOT_FOUND"
            )
        )
    return {
        "success": True,
        "message": "Senha alterada com sucesso"
    }