from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import datetime, date
from typing import Optional
import re

class ClientBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    cpf: Optional[str] = Field(None, description="CPF com 11 dígitos")
    cnpj: Optional[str] = Field(None, description="CNPJ com 14 dígitos")
    email: EmailStr
    endereco: str = Field(..., min_length=5, max_length=200)
    telefone: str = Field(..., min_length=10, max_length=15)
    data_nascimento: date
    perfil: str = Field(..., min_length=2, max_length=50)
    ativo: bool = True

    @field_validator('telefone')
    @classmethod
    def validate_telefone(cls, v):
        phone = re.sub(r'\D', '', v)
        if len(phone) < 10 or len(phone) > 11:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        return phone

    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v):
        if v and len(v) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return v

    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, v):
        if v and v.strip():
            cnpj_clean = re.sub(r'\D', '', v)
            if len(cnpj_clean) != 14:
                raise ValueError('CNPJ deve ter 14 dígitos')
            return cnpj_clean
        return None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    email: Optional[EmailStr] = None
    endereco: Optional[str] = Field(None, min_length=5, max_length=200)
    telefone: Optional[str] = None
    data_nascimento: Optional[date] = None
    perfil: Optional[str] = Field(None, min_length=2, max_length=50)
    ativo: Optional[bool] = None

    @field_validator('telefone')
    @classmethod
    def validate_telefone(cls, v):
        if v:
            phone = re.sub(r'\D', '', v)
            if len(phone) < 10 or len(phone) > 11:
                raise ValueError('Telefone deve ter 10 ou 11 dígitos')
            return phone
        return v

    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v):
        if v and len(v) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return v

    @field_validator('cnpj')
    @classmethod
    def validate_cnpj(cls, v):
        if v and v.strip():
            cnpj_clean = re.sub(r'\D', '', v)
            if len(cnpj_clean) != 14:
                raise ValueError('CNPJ deve ter 14 dígitos')
            return cnpj_clean
        return None

class ClientResponse(ClientBase):
    id_client: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    ativo: bool = True
    
    model_config = {
        "from_attributes": True
    }


class ClientPublic(BaseModel):
    id_client: str
    nome: str
    cpf: Optional[str] = None
    cnpj: Optional[str] = None
    email: EmailStr
    endereco: str
    telefone: str
    data_nascimento: date
    perfil: str
    ativo: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
