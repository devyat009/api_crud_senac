from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models import Product, ProductCreate, ProductUpdate, ProductCategory, ProductCategoryCreate, ProductBrand, ProductBrandCreate

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_codigo_barras(self, codigo_barras: str) -> Optional[Product]:
        """Search product by bar code with category and brand names"""
        product = self.db.query(Product).join(
            ProductCategory, Product.id_categoria == ProductCategory.id_category
        ).join(
            ProductBrand, Product.id_marca == ProductBrand.id_brand
        ).filter(
            Product.codigo_barras == codigo_barras, 
            Product.is_active == True
        ).first()
        
        if product:
            product.nome_categoria = product.categoria.nome_categoria if product.categoria else None
            product.nome_marca = product.marca.nome_marca if product.marca else None
        
        return product
    
    def get_by_codigo_sku(self, codigo_sku: str) -> Optional[Product]:
        """Search product by SKU code with category and brand names"""
        if not codigo_sku:
            return None
        product = self.db.query(Product).join(
            ProductCategory, Product.id_categoria == ProductCategory.id_category
        ).join(
            ProductBrand, Product.id_marca == ProductBrand.id_brand
        ).filter(
            Product.codigo_sku == codigo_sku, 
            Product.is_active == True
        ).first()
        
        if product:
            product.nome_categoria = product.categoria.nome_categoria if product.categoria else None
            product.nome_marca = product.marca.nome_marca if product.marca else None
        
        return product
    
    def get_by_id(self, product_id: str) -> Optional[Product]:
        """Search product by ID with category and brand names"""
        product = self.db.query(Product).join(
            ProductCategory, Product.id_categoria == ProductCategory.id_category
        ).join(
            ProductBrand, Product.id_marca == ProductBrand.id_brand
        ).filter(
            Product.id_product == product_id, 
            Product.is_active == True
        ).first()
        
        if product:
            product.nome_categoria = product.categoria.nome_categoria if product.categoria else None
            product.nome_marca = product.marca.nome_marca if product.marca else None
        
        return product
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """List all active products with category and brand names"""
        products = self.db.query(Product).join(
            ProductCategory, Product.id_categoria == ProductCategory.id_category
        ).join(
            ProductBrand, Product.id_marca == ProductBrand.id_brand
        ).filter(
            Product.is_active == True,
            ProductCategory.is_active == True,
            ProductBrand.is_active == True
        ).offset(skip).limit(limit).all()
        
        # Adiciona os nomes de categoria e marca
        for product in products:
            product.nome_categoria = product.categoria.nome_categoria if product.categoria else None
            product.nome_marca = product.marca.nome_marca if product.marca else None
        
        return products
    
    def get_by_categoria_id(self, categoria_id: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """List products by category ID"""
        products = self.db.query(Product).join(
            ProductCategory, Product.id_categoria == ProductCategory.id_category
        ).join(
            ProductBrand, Product.id_marca == ProductBrand.id_brand
        ).filter(
            Product.id_categoria == categoria_id,
            Product.is_active == True,
            ProductCategory.is_active == True,
            ProductBrand.is_active == True
        ).offset(skip).limit(limit).all()
        
        # Adiciona os nomes de categoria e marca
        for product in products:
            product.nome_categoria = product.categoria.nome_categoria if product.categoria else None
            product.nome_marca = product.marca.nome_marca if product.marca else None
        
        return products
    
    def get_by_marca_id(self, marca_id: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """List products by brand ID"""
        products = self.db.query(Product).join(
            ProductCategory, Product.id_categoria == ProductCategory.id_category
        ).join(
            ProductBrand, Product.id_marca == ProductBrand.id_brand
        ).filter(
            Product.id_marca == marca_id,
            Product.is_active == True,
            ProductCategory.is_active == True,
            ProductBrand.is_active == True
        ).offset(skip).limit(limit).all()
        
        # Adiciona os nomes de categoria e marca
        for product in products:
            product.nome_categoria = product.categoria.nome_categoria if product.categoria else None
            product.nome_marca = product.marca.nome_marca if product.marca else None
        
        return products
    
    def search_products(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """List products by name, model, category or brand name"""
        products = self.db.query(Product).join(
            ProductCategory, Product.id_categoria == ProductCategory.id_category
        ).join(
            ProductBrand, Product.id_marca == ProductBrand.id_brand
        ).filter(
            (Product.nome_item.ilike(f"%{search_term}%") |
             Product.modelo.ilike(f"%{search_term}%") |
             ProductBrand.nome_marca.ilike(f"%{search_term}%") |
             ProductCategory.nome_categoria.ilike(f"%{search_term}%") |
             Product.descricao.ilike(f"%{search_term}%")),
            Product.is_active == True
        ).offset(skip).limit(limit).all()
        
        # Adiciona os nomes de categoria e marca
        for product in products:
            product.nome_categoria = product.categoria.nome_categoria if product.categoria else None
            product.nome_marca = product.marca.nome_marca if product.marca else None
        
        return products
    
    def get_low_stock(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """List low stock products (quantity <= minimum_quantity)"""
        products = self.db.query(Product).join(
            ProductCategory, Product.id_categoria == ProductCategory.id_category
        ).join(
            ProductBrand, Product.id_marca == ProductBrand.id_brand
        ).filter(
            Product.quantidade <= Product.quantidade_minima,
            Product.is_active == True
        ).offset(skip).limit(limit).all()
        
        # Adiciona os nomes de categoria e marca
        for product in products:
            product.nome_categoria = product.categoria.nome_categoria if product.categoria else None
            product.nome_marca = product.marca.nome_marca if product.marca else None
        
        return products
    
    def create(self, product_data: ProductCreate) -> Product:
        """Create new product"""

        # Verify bar code exists
        if self.get_by_codigo_barras(product_data.codigo_barras):
            raise ValueError("Código de barras já está registrado")

        # Verify SKU code exists (if provided)
        if product_data.codigo_sku and self.get_by_codigo_sku(product_data.codigo_sku):
            raise ValueError("Código SKU já está registrado")
            
        # Verify if category exists and is active
        categoria = self.db.query(ProductCategory).filter(
            ProductCategory.id_category == product_data.id_categoria,
            ProductCategory.is_active == True
        ).first()
        if not categoria:
            raise ValueError("Categoria não encontrada ou inativa")
            
        # Verify if brand exists and is active  
        marca = self.db.query(ProductBrand).filter(
            ProductBrand.id_brand == product_data.id_marca,
            ProductBrand.is_active == True
        ).first()
        if not marca:
            raise ValueError("Marca não encontrada ou inativa")
        
        db_product = Product(
            codigo_barras=product_data.codigo_barras,
            nome_item=product_data.nome_item,
            modelo=product_data.modelo,
            codigo_sku=product_data.codigo_sku,
            id_categoria=product_data.id_categoria,
            id_marca=product_data.id_marca,
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
            
            # Adiciona os nomes para retorno
            db_product.nome_categoria = categoria.nome_categoria
            db_product.nome_marca = marca.nome_marca
            
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
        print("Debug - Executando query para categorias")
        categories = self.db.query(ProductCategory).filter(
            ProductCategory.is_active == True
        ).all()
        print(f"Debug - Query retornou {len(categories)} categorias")
        return categories

    def delete_category(self, category_id: str) -> bool:
        """Delete a product category"""
        category = self.db.query(ProductCategory).filter(
            ProductCategory.id_category == category_id
        ).first()
        if not category:
            return False
        category.is_active = False
        self.db.commit()
        return True
      
    def update_category(self, category_id: str, category_update) -> Optional[ProductCategory]:
      db_category = self.db.query(ProductCategory).filter(
          ProductCategory.id_category == category_id
      ).first()
      if not db_category:
          raise ValueError("Categoria não encontrada")
      
      # Verifica se o nome já existe em outra categoria
      existing = self.db.query(ProductCategory).filter(
          ProductCategory.nome_categoria == category_update.nome_categoria,
          ProductCategory.id_category != category_id
      ).first()
      if existing:
          raise ValueError("Já existe uma categoria com esse nome")
      
      db_category.nome_categoria = category_update.nome_categoria
      self.db.commit()
      self.db.refresh(db_category)
      return db_category

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
        print("Debug - Executando query para marcas")
        brands = self.db.query(ProductBrand).filter(
            ProductBrand.is_active == True
        ).all()
        print(f"Debug - Query retornou {len(brands)} marcas")
        return brands

    def delete_brand(self, brand_id: str) -> bool:
        """Delete a product brand"""
        brand = self.db.query(ProductBrand).filter(
            ProductBrand.id_brand == brand_id
        ).first()
        if not brand:
            return False
        brand.is_active = False
        self.db.commit()
        return True

    def update_brand(self, brand_id: str, brand_update) -> Optional[ProductBrand]:
      db_brand = self.db.query(ProductBrand).filter(
          ProductBrand.id_brand == brand_id
      ).first()
      if not db_brand:
          raise ValueError("Marca não encontrada")
      
      # Verifica se o nome já existe em outra marca
      existing = self.db.query(ProductBrand).filter(
          ProductBrand.nome_marca == brand_update.nome_marca,
          ProductBrand.id_brand != brand_id
      ).first()
      if existing:
          raise ValueError("Já existe uma marca com esse nome")
      
      db_brand.nome_marca = brand_update.nome_marca
      self.db.commit()
      self.db.refresh(db_brand)
      return db_brand