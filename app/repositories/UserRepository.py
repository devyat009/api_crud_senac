from datetime import date
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import User, UserCreate, UserUpdate
from passlib.context import CryptContext

# hash config for passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """Password hashing"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify if the password is correct"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Search user by email"""
        return self.db.query(User).filter(User.email == email, User.is_active == True).first()
    
    def get_by_cpf(self, cpf: str) -> Optional[User]:
        """Search user by CPF"""
        return self.db.query(User).filter(User.cpf == cpf, User.is_active == True).first()
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Search user by ID"""
        return self.db.query(User).filter(User.id_user == user_id, User.is_active == True).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all active users"""
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = self.hash_password(user_data.password)
        
        db_user = User(
            email=user_data.email,
            nome=user_data.nome,
            telefone=user_data.telefone,
            data_nascimento=user_data.data_nascimento,
            password_hash=hashed_password,
            cpf=user_data.cpf,
            cnpj=user_data.cnpj if user_data.cnpj and user_data.cnpj.strip() else None
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        db_user = self.get_by_id(user_id)
        
        if not db_user:
            return None

        # Update only the fields that were sent
        update_data = user_data.model_dump(exclude_unset=True)

        # If password was sent, encrypt it
        if "password" in update_data:
            update_data["password_hash"] = self.hash_password(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def delete(self, user_id: str) -> bool:
        """Delete user (soft delete)"""
        db_user = self.get_by_id(user_id)
        
        if not db_user:
            return False
        
        db_user.is_active = False
        self.db.commit()
        
        return True
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = self.get_by_email(email)

        if not user or not self.verify_password(password, user.password_hash):
            return None
        
        return user
    
    def confirm_forgot_password_data(self, email: str, cpf: str, data_nascimento: date) -> Optional[User]:
        """Confirm data for forgot password"""
        user = (
            self.db.query(User)
            .filter(
                User.email == email,
                User.cpf == cpf,
                User.data_nascimento == data_nascimento,
                User.is_active == True
            )
            .first()
        )
        return user

    def change_password(self, user_id: str, new_password: str) -> bool:
        """Change user password"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        user.password_hash = self.hash_password(new_password)
        self.db.commit()
        return True