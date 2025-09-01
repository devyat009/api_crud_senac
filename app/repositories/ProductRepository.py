from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models import Product, ProductCreate, ProductUpdate, ProductCategory, ProductCategoryCreate, ProductBrand, ProductBrandCreate

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_codigo_barras(self, codigo_barras: str) -> Optional[Product]:
        """Search product by bar code"""
        return self.db.query(Product).filter(
            Product.codigo_barras == codigo_barras, 
            Product.is_active == True
        ).first()
    
    def get_by_codigo_sku(self, codigo_sku: str) -> Optional[Product]:
        """Search product by SKU code"""
        if not codigo_sku:
            return None
        return self.db.query(Product).filter(
            Product.codigo_sku == codigo_sku, 
            Product.is_active == True
        ).first()
    
    def get_by_id(self, product_id: str) -> Optional[Product]:
        """Search product by ID"""
        return self.db.query(Product).filter(
            Product.id_product == product_id, 
            Product.is_active == True
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """List all active"""
        return self.db.query(Product).filter(
            Product.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_by_category(self, categoria: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """List products by category"""
        return self.db.query(Product).filter(
            Product.categoria == categoria,
            Product.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_by_marca(self, marca: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """List products by brand"""
        return self.db.query(Product).filter(
            Product.marca == marca,
            Product.is_active == True
        ).offset(skip).limit(limit).all()
    
    def search_products(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """List products by name, model or brand """
        return self.db.query(Product).filter(
            (Product.nome_item.ilike(f"%{search_term}%") |
             Product.modelo.ilike(f"%{search_term}%") |
             Product.marca.ilike(f"%{search_term}%") |
             Product.descricao.ilike(f"%{search_term}%")),
            Product.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_low_stock(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """List low stock products (quantity <= minimum_quantity)"""
        return self.db.query(Product).filter(
            Product.quantidade <= Product.quantidade_minima,
            Product.is_active == True
        ).offset(skip).limit(limit).all()
    
    def create(self, product_data: ProductCreate) -> Product:
        """Create new product"""

        # Verify bar code exists
        if self.get_by_codigo_barras(product_data.codigo_barras):
            raise ValueError("Código de barras já está registrado")

        # Verify SKU code exists (if provided)
        if product_data.codigo_sku and self.get_by_codigo_sku(product_data.codigo_sku):
            raise ValueError("Código SKU já está registrado")
        
        db_product = Product(
            codigo_barras=product_data.codigo_barras,
            nome_item=product_data.nome_item,
            modelo=product_data.modelo,
            codigo_sku=product_data.codigo_sku,
            categoria=product_data.categoria,
            marca=product_data.marca,
            tamanho=product_data.tamanho,
            cor=product_data.cor,
            preco=product_data.preco,
            data=product_data.data,
            quantidade=product_data.quantidade,
            quantidade_minima=product_data.quantidade_minima,
            descricao=product_data.descricao,
            observacoes=product_data.observacoes
        )
        
        try:
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
            
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig).lower()
            
            if "codigo_barras" in error_msg:
                raise ValueError("Código de barras já está registrado")
            elif "codigo_sku" in error_msg:
                raise ValueError("Código SKU já está registrado")
            else:
                raise ValueError("Dados já existem no sistema")
                
        except Exception as e:
            self.db.rollback()
            raise e
    
    def update(self, product_id: str, product_data: ProductUpdate) -> Optional[Product]:
        """Update product"""
        db_product = self.get_by_id(product_id)
        
        if not db_product:
            return None

        # Verify duplicates before updating
        if (product_data.codigo_barras and 
            product_data.codigo_barras != db_product.codigo_barras):
            if self.get_by_codigo_barras(product_data.codigo_barras):
                raise ValueError("Código de barras já está registrado")
        
        if (product_data.codigo_sku and 
            product_data.codigo_sku != db_product.codigo_sku):
            if self.get_by_codigo_sku(product_data.codigo_sku):
                raise ValueError("Código SKU já está registrado")
        
        # Updates only send data
        update_data = product_data.model_dump(exclude_unset=True, exclude_none=True)
        
        try:
            for field, value in update_data.items():
                if hasattr(db_product, field):
                    setattr(db_product, field, value)
            
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
            
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig).lower()
            
            if "codigo_barras" in error_msg:
                raise ValueError("Código de barras já está registrado")
            elif "codigo_sku" in error_msg:
                raise ValueError("Código SKU já está registrado")
            else:
                raise ValueError("Dados já existem no sistema")
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, product_id: str) -> bool:
        """Delete product (soft delete)"""
        db_product = self.get_by_id(product_id)
        
        if not db_product:
            return False
        
        try:
            db_product.is_active = False
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise ValueError("Erro ao deletar produto")
    
    def update_stock(self, product_id: str, new_quantity: int) -> Optional[Product]:
        """Update product stock"""
        db_product = self.get_by_id(product_id)
        
        if not db_product:
            return None
        
        if new_quantity < 0:
            raise ValueError("Quantidade não pode ser negativa")
        
        try:
            db_product.quantidade = new_quantity
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
        except Exception as e:
            self.db.rollback()
            raise e
          
    # --- CATEGORY ---
    def create_category(self, category_data):
        """Create a new product category"""
        # Verifica se já existe
        existing = self.db.query(ProductCategory).filter(
            ProductCategory.nome_categoria == category_data.nome_categoria
        ).first()
        if existing:
            raise ValueError("Categoria já cadastrada")
        db_category = ProductCategory(
            nome_categoria=category_data.nome_categoria
        )
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def get_all_categories(self):
        """List all product categories"""
        return self.db.query(ProductCategory).all()

    def delete_category(self, category_id: str) -> bool:
        """Delete a product category"""
        category = self.db.query(ProductCategory).filter(
            ProductCategory.id_category == category_id
        ).first()
        if not category:
            return False
        self.db.delete(category)
        self.db.commit()
        return True

    # --- BRAND ---
    def create_brand(self, brand_data):
        """Create a new product brand"""
        existing = self.db.query(ProductBrand).filter(
            ProductBrand.nome_marca == brand_data.nome_marca
        ).first()
        if existing:
            raise ValueError("Marca já cadastrada")
        db_brand = ProductBrand(
            nome_marca=brand_data.nome_marca
        )
        self.db.add(db_brand)
        self.db.commit()
        self.db.refresh(db_brand)
        return db_brand

    def get_all_brands(self):
        """List all product brands"""
        return self.db.query(ProductBrand).all()

    def delete_brand(self, brand_id: str) -> bool:
        """Delete a product brand"""
        brand = self.db.query(ProductBrand).filter(
            ProductBrand.id_brand == brand_id
        ).first()
        if not brand:
            return False
        self.db.delete(brand)
        self.db.commit()
        return True
