from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import UserCreate, UserUpdate, UserResponse, UserLogin
from app.repositories.UserRepository import UserRepository
from app.utils.ErrorModel import create_error_response


router = APIRouter()

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Dependency injection do repository"""
    return UserRepository(db)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, repo: UserRepository = Depends(get_user_repository)):
    """Create a new user"""
    
    try:
        if repo.get_by_email(user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(
                    message="Email já está registrado",
                    field="email",
                    code="EMAIL_ALREADY_EXISTS"
                )
            )
        
        if user.cpf and repo.get_by_cpf(user.cpf):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(
                    message="CPF já está registrado",
                    field="cpf",
                    code="CPF_ALREADY_EXISTS"
                )
            )
        
        return repo.create(user)
        
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

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, repo: UserRepository = Depends(get_user_repository)):
    """Listar todos os usuários"""
    try:
        return repo.get_all(skip=skip, limit=limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                message="Erro ao listar usuários",
                code="LIST_USERS_ERROR"
            )
        )

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, repo: UserRepository = Depends(get_user_repository)):
    """Obter um usuário específico"""
    try:
        user = repo.get_by_id(user_id)
    
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    message="Nenhum usuário encontrado",
                    code="USERS_NOT_FOUND"
                )
            )
        return user
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                message="Erro ao buscar usuário",
                code="GET_USER_ERROR"
            )
        )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_update: UserUpdate, repo: UserRepository = Depends(get_user_repository)):
    """Atualizar um usuário"""
    try: 
        user = repo.update(user_id, user_update)
    
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    message="Usuário não encontrado",
                    field="user_id",
                    code="USER_NOT_FOUND"
                )
            )
    
        return user
    
    except HTTPException:
        raise
    except ValueError as e:
        # Repository validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                message=str(e),
                code="VALIDATION_ERROR"
            )
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                message="Erro ao atualizar usuário",
                code="UPDATE_USER_ERROR"
            )
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, repo: UserRepository = Depends(get_user_repository)):
    """Deletar um usuário (soft delete)"""
    try:
        success = repo.delete(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response(
                    message="Usuário não encontrado",
                    field="user_id",
                    code="USER_NOT_FOUND"
                )
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response(
                message="Erro ao deletar usuário",
                code="DELETE_USER_ERROR"
            )
        )