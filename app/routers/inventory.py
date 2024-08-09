from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import MetaData
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from io import BytesIO
import pandas as pd
from app.database import get_db
from app.models import Inventory, Product, Warehouse, City

router = APIRouter()

@router.post("/upload/")
async def upload_inventory_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise HTTPException(status_code=400, detail="Invalid file format. Only Excel files are supported.")
    content = await file.read()
    df = pd.read_excel(BytesIO(content))

    for _, row in df.iterrows():
        product_code = row['Malzeme']
        product_name = row['Malzeme Tanım']
        depo_y = row['DepoY.']
        uniq_id = row['UNIQID']
        quantity = row['Toplam Miktar']

        city_code = depo_y[:2]
        warehouse_code = depo_y

        city = db.query(City).filter_by(city_code=city_code).first()
        if not city:
            city = City(city_code=city_code, city_name=f"City {city_code}")
            db.add(city)
            db.commit()

        warehouse = db.query(Warehouse).filter_by(warehouse_code=warehouse_code).first()
        if not warehouse:
            warehouse = Warehouse(warehouse_code=warehouse_code, warehouse_name=f"Warehouse {warehouse_code}", city_code=city_code)
            db.add(warehouse)
            db.commit()

        product = db.query(Product).filter_by(product_code=product_code).first()
        if not product:
            product = Product(product_code=product_code, product_name=product_name, unit_price=0)
            db.add(product)
            db.commit()

        db.execute(text(f"""
            INSERT INTO inventory (inventory_code, product_code, warehouse_code, quantity, timestamp)
            VALUES (:inventory_code, :product_code, :warehouse_code, :quantity, :timestamp)
        """), {
            "inventory_code": uniq_id,
            "product_code": product_code,
            "warehouse_code": warehouse_code,
            "quantity": quantity,
            "timestamp": pd.Timestamp.now()
        })
        db.commit()

    return {"status": "Inventory data uploaded successfully"}

@router.get("/{warehouse_code}")
async def get_warehouse_inventory(warehouse_code: str, db: Session = Depends(get_db)):
    query = text(f"""
        SELECT * FROM inventory
        WHERE warehouse_code = :warehouse_code
    """)
    result = db.execute(query, {"warehouse_code": warehouse_code}).fetchall()

    metadata = MetaData()
    metadata.reflect(bind=db.get_bind())
    column_names = metadata.tables['inventory'].columns.keys()

    data = [
        dict(zip(column_names, row))
        for row in result
    ]

    return data
