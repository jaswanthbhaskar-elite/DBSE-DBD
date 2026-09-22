from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker


# -------------------------
# Database setup
# -------------------------

Base = declarative_base()


class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)


DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/product_management_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# -------------------------
# FastAPI setup
# -------------------------

app = FastAPI(
    title="Product Management System",
    version="1.0.0"
)


# -------------------------
# Product model
# -------------------------

class Product(BaseModel):
    name: str
    description: str
    price: float
    quantity: int


# -------------------------
# Home
# -------------------------

@app.get("/")
def home():
    return {
        "message": "Product Management System API is running"
    }


# -------------------------
# GET all products
# -------------------------

@app.get("/products")
def get_products(db=Depends(get_db)):
    products = db.query(ProductDB).all()

    return {
        "products": products
    }


# -------------------------
# POST create product
# -------------------------

@app.post("/products", status_code=201)
def create_product(product: Product, db=Depends(get_db)):

    new_product = ProductDB(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product created successfully",
        "product": new_product
    }


# -------------------------
# GET product by ID
# -------------------------

@app.get("/products/{product_id}")
def get_product(product_id: int, db=Depends(get_db)):

    product = db.query(ProductDB).filter(
        ProductDB.id == product_id
    ).first()

    if not product:
        return {
            "message": "Product not found"
        }

    return {
        "product": product
    }


# -------------------------
# PUT update product
# -------------------------

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: Product,
    db=Depends(get_db)
):

    existing_product = db.query(ProductDB).filter(
        ProductDB.id == product_id
    ).first()

    if not existing_product:
        return {
            "message": "Product not found"
        }

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.quantity = product.quantity

    db.commit()
    db.refresh(existing_product)

    return {
        "message": "Product updated successfully",
        "product": existing_product
    }


# -------------------------
# PATCH update product
# -------------------------

@app.patch("/products/{product_id}")
def partial_update_product(
    product_id: int,
    product: Product,
    db=Depends(get_db)
):

    existing_product = db.query(ProductDB).filter(
        ProductDB.id == product_id
    ).first()

    if not existing_product:
        return {
            "message": "Product not found"
        }

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.quantity = product.quantity

    db.commit()
    db.refresh(existing_product)

    return {
        "message": "Product partially updated successfully",
        "product": existing_product
    }


# -------------------------
# DELETE product
# -------------------------

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db=Depends(get_db)):

    existing_product = db.query(ProductDB).filter(
        ProductDB.id == product_id
    ).first()

    if not existing_product:
        return {
            "message": "Product not found"
        }

    deleted_product = {
        "id": existing_product.id,
        "name": existing_product.name,
        "description": existing_product.description,
        "price": existing_product.price,
        "quantity": existing_product.quantity
    }

    db.delete(existing_product)
    db.commit()

    return {
        "message": "Product deleted successfully",
        "product": deleted_product
    }