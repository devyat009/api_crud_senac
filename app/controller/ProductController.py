from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import ProductCreate, ProductUpdate, ProductResponse
from app.repositories.ProductRepository import ProductRepository
from datetime import datetime

router = APIRouter(prefix="/api/v1/products", tags=["Products"])

def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)

@router.post("/", response_model=dict)
async def create_product(
    product: ProductCreate,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Create new product"""
    try:
        db_product = repository.create(product)
        return {
            "success": True,
            "message": "Produto criado com sucesso",
            "data": ProductResponse.model_validate(db_product),
            "timestamp": datetime.utcnow().isoformat()
        }
    except ValueError as e:
        return {
            "success": False,
            "message": str(e),
            "field": "codigo_barras" if "código de barras" in str(e).lower() else "codigo_sku" if "sku" in str(e).lower() else None,
            "code": "DUPLICATE_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Erro interno do servidor",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/", response_model=dict)
async def get_products(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de registros"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    marca: Optional[str] = Query(None, description="Filtrar por marca"),
    search: Optional[str] = Query(None, description="Buscar produtos"),
    low_stock: bool = Query(False, description="Produtos com estoque baixo"),
    repository: ProductRepository = Depends(get_product_repository)
):
    """List products with optional filters"""
    try:
        if low_stock:
            products = repository.get_low_stock(skip, limit)
        elif search:
            products = repository.search_products(search, skip, limit)
        elif categoria:
            products = repository.get_by_category(categoria, skip, limit)
        elif marca:
            products = repository.get_by_marca(marca, skip, limit)
        else:
            products = repository.get_all(skip, limit)
        
        products_response = [ProductResponse.model_validate(product) for product in products]
        
        return {
            "success": True,
            "message": f"Encontrados {len(products_response)} produtos",
            "data": products_response,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": len(products_response)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": "Erro interno do servidor",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/{product_id}", response_model=dict)
async def get_product(
    product_id: str,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Search product by ID"""
    try:
        product = repository.get_by_id(product_id)
        
        if not product:
            return {
                "success": False,
                "message": "Produto não encontrado",
                "code": "NOT_FOUND",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "message": "Produto encontrado",
            "data": ProductResponse.model_validate(product),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": "Erro interno do servidor",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/barcode/{codigo_barras}", response_model=dict)
async def get_product_by_barcode(
    codigo_barras: str,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Search product by barcode"""
    try:
        product = repository.get_by_codigo_barras(codigo_barras)
        
        if not product:
            return {
                "success": False,
                "message": "Produto não encontrado",
                "code": "NOT_FOUND",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "message": "Produto encontrado",
            "data": ProductResponse.model_validate(product),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": "Erro interno do servidor",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/sku/{codigo_sku}", response_model=dict)
async def get_product_by_sku(
    codigo_sku: str,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Search product by SKU code"""
    try:
        product = repository.get_by_codigo_sku(codigo_sku)
        
        if not product:
            return {
                "success": False,
                "message": "Produto não encontrado",
                "code": "NOT_FOUND",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "message": "Produto encontrado",
            "data": ProductResponse.model_validate(product),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": "Erro interno do servidor",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.put("/{product_id}", response_model=dict)
async def update_product(
    product_id: str,
    product: ProductUpdate,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Update product"""
    try:
        db_product = repository.update(product_id, product)
        
        if not db_product:
            return {
                "success": False,
                "message": "Produto não encontrado",
                "code": "NOT_FOUND",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "message": "Produto atualizado com sucesso",
            "data": ProductResponse.model_validate(db_product),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        return {
            "success": False,
            "message": str(e),
            "field": "codigo_barras" if "código de barras" in str(e).lower() else "codigo_sku" if "sku" in str(e).lower() else None,
            "code": "DUPLICATE_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Erro interno do servidor",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.patch("/{product_id}/stock", response_model=dict)
async def update_product_stock(
    product_id: str,
    quantity: int = Query(..., ge=0, description="Nova quantidade em estoque"),
    repository: ProductRepository = Depends(get_product_repository)
):
    """Update product stock"""
    try:
        db_product = repository.update_stock(product_id, quantity)
        
        if not db_product:
            return {
                "success": False,
                "message": "Produto não encontrado",
                "code": "NOT_FOUND",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "message": "Estoque atualizado com sucesso",
            "data": ProductResponse.model_validate(db_product),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValueError as e:
        return {
            "success": False,
            "message": str(e),
            "code": "VALIDATION_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Erro interno do servidor",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.delete("/{product_id}", response_model=dict)
async def delete_product(
    product_id: str,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Delete product (soft delete)"""
    try:
        success = repository.delete(product_id)
        
        if not success:
            return {
                "success": False,
                "message": "Produto não encontrado",
                "code": "NOT_FOUND",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "message": "Produto deletado com sucesso",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": "Erro interno do servidor",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
