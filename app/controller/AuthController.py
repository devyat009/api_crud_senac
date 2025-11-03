from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from app.controller.UserController import get_user_repository
from app.database import get_db
from app.models import *
from app.repositories.UserRepository import UserRepository
from app.utils.ErrorModel import create_error_response
from pydantic import BaseModel
import httpx
import os
import uuid

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


class GoogleLoginRequest(BaseModel):
    token: str


def _verify_google_token(id_token: str) -> dict:
    """Valida o ID Token do Google via endpoint tokeninfo.
    Retorna o payload (claims) se válido; lança HTTPException se inválido.
    """
    try:
        resp = httpx.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
            timeout=10.0,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                message="Falha ao validar token do Google",
                code="INVALID_GOOGLE_TOKEN",
            ),
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                message="Token do Google inválido",
                code="INVALID_GOOGLE_TOKEN",
            ),
        )

    claims = resp.json()

    # Valida audiência se variável de ambiente estiver configurada
    expected_aud = os.getenv("GOOGLE_CLIENT_ID")
    if expected_aud and claims.get("aud") != expected_aud:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                message="Token do Google não corresponde ao Client ID configurado",
                code="INVALID_GOOGLE_AUDIENCE",
            ),
        )

    # Checa e-mail verificado (quando disponível)
    if str(claims.get("email_verified", "false")).lower() not in ("true", "1"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_error_response(
                message="E-mail do Google não verificado",
                code="EMAIL_NOT_VERIFIED",
            ),
        )

    if not claims.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                message="Token do Google sem e-mail",
                code="GOOGLE_TOKEN_NO_EMAIL",
            ),
        )

    return claims


@router.post("/google")
def login_with_google(
    payload: GoogleLoginRequest,
    repo: UserRepository = Depends(get_user_repository)
):
    """Autentica com Google. Se o usuário não existir, cria automaticamente.
    Retorna o mesmo formato do login normal.
    """
    claims = _verify_google_token(payload.token)

    email = claims.get("email")
    nome = (
        claims.get("name")
        or f"{claims.get('given_name', '')} {claims.get('family_name', '')}".strip()
        or email.split("@")[0]
    )

    # Tenta obter usuário ativo
    user = repo.get_by_email(email)

    if not user:
        # Se não existir, cria com dados mínimos válidos
        # Campos obrigatórios no modelo: telefone, data_nascimento, password
        random_password = uuid.uuid4().hex + "Gg1!"
        try:
            user_create = UserCreate(
                email=email,
                nome=nome,
                telefone="00000000000",
                data_nascimento=date(1970, 1, 1),
                role="user",
                password=random_password,
                confirm_password=random_password,
                cpf=None,
                cnpj=None,
            )
            user = repo.create(user_create)
        except Exception:
            # Caso exista um usuário inativo com o mesmo e-mail, tenta reativar
            # Busca sem filtrar por ativo
            from app.models.models import User as UserModel

            existing = repo.db.query(UserModel).filter(UserModel.email == email).first()
            if existing:
                existing.is_active = True
                if not existing.password_hash:
                    existing.password_hash = repo.hash_password(random_password)
                if not existing.telefone:
                    existing.telefone = "00000000000"
                if not existing.data_nascimento:
                    existing.data_nascimento = date(1970, 1, 1)
                repo.db.commit()
                repo.db.refresh(existing)
                user = existing
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=create_error_response(
                        message="Não foi possível criar usuário com Google",
                        code="GOOGLE_SIGNUP_ERROR",
                    ),
                )

    return {
        "success": True,
        "message": "Login realizado com Google",
        "user_id": user.id_user,
        "email": user.email,
        "nome": user.nome,
        "role": user.role,
    }