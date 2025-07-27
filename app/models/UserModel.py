from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import datetime, date
from typing import Optional
import re

class UserBase(BaseModel):
    """Base schema for user data"""
    email: EmailStr
    nome: str = Field(..., min_length=2, max_length=100)
    telefone: str = Field(..., min_length=10, max_length=15)
    data_nascimento: date
    
    @field_validator('telefone')
    @classmethod
    def validate_telefone(cls, v):
        phone = re.sub(r'\D', '', v)
        if len(phone) < 10 or len(phone) > 11:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        return phone

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserCreate(UserBase):
    """Schema for user creation"""
    senha: str = Field(..., min_length=8, description="Mínimo 8 caracteres")
    confirm_password: str
    cpf: Optional[str] = Field(None, pattern=r'^\d{11}$')
    cnpj: Optional[str] = Field(None, pattern=r'^\d{14}$')

    @model_validator(mode='after')
    def passwords_match(self):
        if self.senha != self.confirm_password:
            raise ValueError('Senhas não coincidem')
        return self
    
    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v):
        if v and len(v) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return v
    
    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, v):
        if v and len(v) != 14:
            raise ValueError('CNPJ deve ter 14 dígitos')
        return v

class UserUpdate(BaseModel):
    """Schema for update - all fields are optional"""
    email: Optional[EmailStr] = None
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    telefone: Optional[str] = None
    data_nascimento: Optional[date] = None
    senha: Optional[str] = Field(None, min_length=8)
    cpf: Optional[str] = Field(None, pattern=r'^\d{11}$')
    cnpj: Optional[str] = Field(None, pattern=r'^\d{14}$')
    
    @field_validator('telefone')
    @classmethod
    def validate_telefone(cls, v):
        if v:  # Só valida se não for None
            phone = re.sub(r'\D', '', v)
            if len(phone) < 10 or len(phone) > 11:
                raise ValueError('Telefone deve ter 10 ou 11 dígitos')
            return phone
        return v

class UserResponse(UserBase):
    """Schema for API response"""
    id_user: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    model_config = {
        "from_attributes": True
    }

class UserPublic(BaseModel):
    """Schema for public user data (without sensitive information)"""
    id_user: str 
    nome: str
    email: EmailStr
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }