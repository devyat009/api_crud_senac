import uuid
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Float, Text
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id_user = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Senha criptografada
    nome = Column(String(100), nullable=False)
    telefone = Column(String(15), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    cpf = Column(String(11), unique=True, nullable=True, index=True)
    cnpj = Column(String(14), nullable=True, index=True)
    
    # Campos de controle
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Product(Base):
    __tablename__ = "products"
    
    id_product = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    codigo_barras = Column(String(50), unique=True, index=True, nullable=False)
    nome_item = Column(String(200), nullable=False, index=True)
    modelo = Column(String(100), nullable=False)
    codigo_sku = Column(String(50), nullable=True, index=True)
    categoria = Column(String(50), nullable=False, index=True)
    marca = Column(String(100), nullable=False, index=True)
    tamanho = Column(String(50), nullable=True)
    cor = Column(String(50), nullable=True)
    preco = Column(Float, nullable=False)
    data = Column(Date, nullable=True)
    quantidade = Column(Integer, nullable=False, default=0)
    quantidade_minima = Column(Integer, nullable=False, default=0)
    descricao = Column(Text, nullable=True)
    observacoes = Column(Text, nullable=True)
    
    # Campos de controle
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())