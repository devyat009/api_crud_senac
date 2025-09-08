from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import ProductCreate, ProductUpdate, ProductResponse
from app.models.ProductModel import *
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

# === CATEGORY AND BRAND ROUTES (must be before /{product_id}) ===
@router.post('/category', response_model=dict)
async def create_product_category(
    category: ProductCategoryCreate,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Create a new product category"""
    try:
        db_category = repository.create_category(category)
        return {
            "success": True,
            "message": "Categoria criada com sucesso",
            "data": ProductCategoryResponse.model_validate(db_category),
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

@router.get('/category', response_model=dict)
async def get_product_categories(
    repository: ProductRepository = Depends(get_product_repository)
):
    """Get all product categories"""
    try:
        db_categories = repository.get_all_categories()
        # print(f"Debug - Categorias encontradas: {len(db_categories)}")
        # print(f"Debug - Primeira categoria: {db_categories[0].__dict__ if db_categories else 'Nenhuma'}")
        
        if not db_categories:
            return {
                "success": False,
                "message": "Nenhuma categoria encontrada",
                "code": "NOT_FOUND",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "message": f"Encontradas {len(db_categories)} categorias",
            "data": [ProductCategoryResponse.model_validate(cat) for cat in db_categories],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Debug - Erro: {str(e)}")
        return {
            "success": False,
            "message": f"Erro interno do servidor: {str(e)}",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.delete('/category/{category_id}', response_model=dict)
async def delete_product_category(
    category_id: str,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Delete product category"""
    try:
        success = repository.delete_category(category_id)
        if not success:
            return {
                "success": False,
                "message": "Categoria não encontrada",
                "code": "NOT_FOUND",
                "timestamp": datetime.utcnow().isoformat()
            }
        return {
            "success": True,
            "message": "Categoria deletada com sucesso",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Erro interno do servidor",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
        
@router.patch('/category/{category_id}', response_model=dict)
async def update_product_category(
    category_id: str,
    category: ProductCategoryUpdate,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Update product category"""
    try:
        db_category = repository.update_category(category_id, category)
        return {
            "success": True,
            "message": "Categoria atualizada com sucesso",
            "data": ProductCategoryResponse.model_validate(db_category),
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

@router.post('/brand', response_model=dict)
async def create_product_brand(
    brand: ProductBrandCreate,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Create a new product brand"""
    try:
        db_brand = repository.create_brand(brand)
        return {
            "success": True,
            "message": "Marca criada com sucesso",
            "data": ProductBrandResponse.model_validate(db_brand),
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

@router.get('/brand', response_model=dict)
async def get_product_brands(
    repository: ProductRepository = Depends(get_product_repository)
):
    """Get all product brands"""
    try:
        db_brands = repository.get_all_brands()
        # print(f"Debug - Marcas encontradas: {len(db_brands)}")
        # print(f"Debug - Primeira marca: {db_brands[0].__dict__ if db_brands else 'Nenhuma'}")
        
        if not db_brands:
            return {
                "success": False,
                "message": "Nenhuma marca encontrada",
                "code": "NOT_FOUND",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "message": f"Encontradas {len(db_brands)} marcas",
            "data": [ProductBrandResponse.model_validate(brand) for brand in db_brands],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Debug - Erro: {str(e)}")
        return {
            "success": False,
            "message": f"Erro interno do servidor: {str(e)}",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }

@router.delete('/brand/{brand_id}', response_model=dict)
async def delete_product_brand(
    brand_id: str,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Delete product brand"""
    try:
        success = repository.delete_brand(brand_id)
        if not success:
            return {
                "success": False,
                "message": "Marca não encontrada",
                "code": "NOT_FOUND",
                "timestamp": datetime.utcnow().isoformat()
            }
        return {
            "success": True,
            "message": "Marca deletada com sucesso",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Erro interno do servidor",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
        
@router.patch('/brand/{brand_id}', response_model=dict)
async def update_product_brand(
    brand_id: str,
    brand: ProductBrandUpdate,
    repository: ProductRepository = Depends(get_product_repository)
):
    """Update product brand"""
    try:
        db_brand = repository.update_brand(brand_id, brand)
        return {
            "success": True,
            "message": "Marca atualizada com sucesso",
            "data": ProductBrandResponse.model_validate(db_brand),
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

# === PRODUCT ROUTES ===
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
