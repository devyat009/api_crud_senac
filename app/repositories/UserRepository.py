from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import User, UserCreate, UserUpdate
from passlib.context import CryptContext

# Configuração para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """Criptografa a senha"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha está correta"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Buscar usuário por email"""
        return self.db.query(User).filter(User.email == email, User.is_active == True).first()
    
    def get_by_cpf(self, cpf: str) -> Optional[User]:
        """Buscar usuário por CPF"""
        return self.db.query(User).filter(User.cpf == cpf, User.is_active == True).first()
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Buscar usuário por ID"""
        return self.db.query(User).filter(User.id_user == user_id, User.is_active == True).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Listar todos os usuários ativos"""
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def create(self, user_data: UserCreate) -> User:
        """Criar novo usuário"""
        hashed_password = self.hash_password(user_data.senha)
        
        db_user = User(
            email=user_data.email,
            nome=user_data.nome,
            telefone=user_data.telefone,
            data_nascimento=user_data.data_nascimento,
            senha_hash=hashed_password,
            cpf=user_data.cpf,
            cnpj=user_data.cnpj
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Atualizar usuário"""
        db_user = self.get_by_id(user_id)
        
        if not db_user:
            return None
        
        # Atualizar apenas os campos enviados
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Se senha foi enviada, criptografar
        if "senha" in update_data:
            update_data["senha_hash"] = self.hash_password(update_data.pop("senha"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def delete(self, user_id: str) -> bool:
        """Deletar usuário (soft delete)"""
        db_user = self.get_by_id(user_id)
        
        if not db_user:
            return False
        
        db_user.is_active = False
        self.db.commit()
        
        return True
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Autenticar usuário"""
        user = self.get_by_email(email)
        
        if not user or not self.verify_password(password, user.senha_hash):
            return None
        
        return user