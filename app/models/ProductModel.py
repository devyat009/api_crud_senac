from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional
import re

class ProductBase(BaseModel):
    """Base schema for product data"""
    codigo_barras: str = Field(..., description="Código de barras do produto")
    nome_item: str = Field(..., min_length=2, max_length=200, description="Nome do produto")
    modelo: str = Field(..., min_length=1, max_length=100, description="Modelo do produto")
    codigo_sku: Optional[str] = Field(None, description="Código SKU (opcional)")
    categoria: str = Field(..., description="Categoria do produto")
    marca: str = Field(..., description="Marca do produto")
    tamanho: Optional[str] = Field(None, description="Tamanho do produto (opcional)")
    cor: Optional[str] = Field(None, description="Cor do produto (opcional)")
    preco: float = Field(..., ge=0, description="Preço do produto")
    data: Optional[date] = Field(None, description="Data de cadastro/validade")
    quantidade: int = Field(..., ge=0, description="Quantidade em estoque")
    quantidade_minima: int = Field(..., ge=0, description="Quantidade mínima em estoque")
    descricao: Optional[str] = Field(None, description="Descrição do produto")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    
    @field_validator('codigo_barras')
    @classmethod
    def validate_codigo_barras(cls, v):
        if not v or not v.strip():
            raise ValueError('Código de barras é obrigatório')
        # Remove caracteres não numéricos
        codigo_clean = re.sub(r'\D', '', v)
        if len(codigo_clean) < 8:
            raise ValueError('Código de barras deve ter pelo menos 8 dígitos')
        return v.strip()
    
    @field_validator('nome_item')
    @classmethod
    def validate_nome_item(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome do item é obrigatório')
        return v.strip()
    
    @field_validator('modelo')
    @classmethod
    def validate_modelo(cls, v):
        if not v or not v.strip():
            raise ValueError('Modelo é obrigatório')
        return v.strip()
    
    @field_validator('categoria')
    @classmethod
    def validate_categoria(cls, v):
        categorias_validas = ['eletronicos', 'roupas', 'casa', 'esportes', 'livros', 'outros']
        if v not in categorias_validas:
            raise ValueError(f'Categoria deve ser uma das: {", ".join(categorias_validas)}')
        return v
    
    @field_validator('marca')
    @classmethod
    def validate_marca(cls, v):
        if not v or not v.strip():
            raise ValueError('Marca é obrigatória')
        return v.strip()
    
    @field_validator('preco')
    @classmethod
    def validate_preco(cls, v):
        if v is None or v < 0:
            raise ValueError('Preço deve ser maior ou igual a zero')
        return round(v, 2)

class ProductCreate(ProductBase):
    """Schema for product creation"""
    pass

class ProductUpdate(BaseModel):
    """Schema for product update - all fields are optional"""
    codigo_barras: Optional[str] = None
    nome_item: Optional[str] = Field(None, min_length=2, max_length=200)
    modelo: Optional[str] = Field(None, min_length=1, max_length=100)
    codigo_sku: Optional[str] = None
    categoria: Optional[str] = None
    marca: Optional[str] = None
    tamanho: Optional[str] = None
    cor: Optional[str] = None
    preco: Optional[float] = Field(None, ge=0)
    data: Optional[date] = None
    quantidade: Optional[int] = Field(None, ge=0)
    quantidade_minima: Optional[int] = Field(None, ge=0)
    descricao: Optional[str] = None
    observacoes: Optional[str] = None
    
    @field_validator('categoria')
    @classmethod
    def validate_categoria(cls, v):
        if v:
            categorias_validas = ['eletronicos', 'roupas', 'casa', 'esportes', 'livros', 'outros']
            if v not in categorias_validas:
                raise ValueError(f'Categoria deve ser uma das: {", ".join(categorias_validas)}')
        return v
    
    @field_validator('preco')
    @classmethod
    def validate_preco(cls, v):
        if v is not None and v < 0:
            raise ValueError('Preço deve ser maior ou igual a zero')
        return round(v, 2) if v is not None else v

class ProductResponse(ProductBase):
    """Schema for API response"""
    id_product: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    model_config = {
        "from_attributes": True
    }

class ProductPublic(BaseModel):
    """Schema for public product data"""
    id_product: str 
    nome_item: str
    modelo: str
    categoria: str
    marca: str
    preco: float
    quantidade: int
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }
  
  
class ProductCategoryBase(BaseModel):
    """Schema for product category data"""
    nome_categoria: str

class ProductCategoryCreate(ProductCategoryBase):
    """Schema for product creation"""
    pass

class ProductCategoryResponse(ProductCategoryBase):
    """Schema for product category response"""
    id_category: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class ProductBrandBase(BaseModel):
    """Schema for product brand data"""
    nome_marca: str

class ProductBrandCreate(ProductBrandBase):
    """Schema for product creation"""
    pass

class ProductBrandResponse(ProductBrandBase):
    """Schema for product brand response"""
    id_brand: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
    
