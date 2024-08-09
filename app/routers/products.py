from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from io import BytesIO
import pandas as pd
from app.database import get_db
from app.models import Product
from app.schemas import Product as ProductSchema, ProductCreate

router = APIRouter()


@router.post("/upload/")
async def upload_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise HTTPException(status_code=400, detail="Invalid file format. Only Excel files are supported.")

    content = await file.read()
    df = pd.read_excel(BytesIO(content))

    # Check if necessary columns are present
    if not {'Malzeme', 'Malzeme Tanım'}.issubset(df.columns):
        raise HTTPException(status_code=400, detail="Excel file is missing required columns.")

    for _, row in df.iterrows():
        product_code = row.get('Malzeme')
        product_name = row.get('Malzeme Tanım')
        if not product_code or not product_name:
            continue  # Skip rows with missing data

        product = db.query(Product).filter_by(product_code=product_code).first()
        if not product:
            product = Product(product_code=product_code, product_name=product_name, unit_price=0)
            db.add(product)
            db.commit()

    return {"status": "Products uploaded successfully"}


@router.post("/create/", response_model=ProductSchema)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    existing_product = db.query(Product).filter_by(product_code=product.product_code).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product already exists.")

    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/products/", response_model=List[ProductSchema])
async def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@router.get("/product/{product_code}", response_model=ProductSchema)
async def get_product(product_code: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter_by(product_code=product_code).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product


@router.delete("/delete/{product_code}")
async def delete_product(product_code: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter_by(product_code=product_code).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    db.delete(product)
    db.commit()
    return {"status": "Product deleted successfully"}

@router.put("/update/{product_code}", response_model=ProductSchema)
async def update_product(product_code: str, product: ProductCreate, db: Session = Depends(get_db)):
    # Query to find the product by code
    db_product = db.query(Product).filter(Product.product_code == product_code).first()

    # Check if the product exists
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update the product attributes
    for key, value in product.dict().items():
        setattr(db_product, key, value)

    # Commit changes to the database
    db.commit()
    db.refresh(db_product)

    return db_product