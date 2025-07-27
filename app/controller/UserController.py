from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import UserCreate, UserUpdate, UserResponse, UserLogin
from app.repositories.UserRepository import UserRepository


router = APIRouter()

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Dependency injection do repository"""
    return UserRepository(db)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, repo: UserRepository = Depends(get_user_repository)):
    """Criar um novo usuário"""
    
    # Verificar se email já existe
    if repo.get_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está registrado"
        )
    
    # Verificar se CPF já existe
    if user.cpf and repo.get_by_cpf(user.cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já está registrado"
        )
    
    return repo.create(user)

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, repo: UserRepository = Depends(get_user_repository)):
    """Listar todos os usuários"""
    return repo.get_all(skip, limit)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, repo: UserRepository = Depends(get_user_repository)):
    """Obter um usuário específico"""
    user = repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_update: UserUpdate, repo: UserRepository = Depends(get_user_repository)):
    """Atualizar um usuário"""
    user = repo.update(user_id, user_update)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, repo: UserRepository = Depends(get_user_repository)):
    """Deletar um usuário (soft delete)"""
    success = repo.delete(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )