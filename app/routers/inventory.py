from io import BytesIO

import pandas as pd
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from fastapi.logger import logger
from sqlalchemy.orm import Session
from sqlalchemy import or_, text, delete
from typing import List, Optional
from app.models import Product, Warehouse, Inventory, City
from app.schemas import InventoryCreate, Inventory as InventorySchema, PaginatedResponse
from app.database import get_db

router = APIRouter()

class InventoryResponse(InventorySchema):
    data: List[InventorySchema]
    class Config:
        orm_mode = True

@router.post("/upload/")
async def upload_inventory_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            raise HTTPException(status_code=400, detail="Invalid file format. Only Excel files are supported.")

        content = await file.read()
        df = pd.read_excel(BytesIO(content))

        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded file is empty or not in the expected format.")

        # Clear existing inventory data
        db.execute(delete(Inventory))
        db.commit()

        # Process new inventory data
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
                warehouse = Warehouse(warehouse_code=warehouse_code, warehouse_name=f"Warehouse {warehouse_code}",
                                      city_code=city_code)
                db.add(warehouse)
                db.commit()

            product = db.query(Product).filter_by(product_code=product_code).first()
            if not product:
                product = Product(product_code=product_code, product_name=product_name, unit_price=0)
                db.add(product)
                db.commit()

            # Insert new inventory data
            db.execute(text(f"""
                INSERT INTO inventory (inventory_code, product_code, warehouse_code, quantity, timestamp)
                VALUES (:inventory_code, :product_code, :warehouse_code, :quantity, :timestamp)
                ON DUPLICATE KEY UPDATE 
                product_code=VALUES(product_code),
                warehouse_code=VALUES(warehouse_code),
                quantity=VALUES(quantity),
                timestamp=VALUES(timestamp)
            """), {
                "inventory_code": uniq_id,
                "product_code": product_code,
                "warehouse_code": warehouse_code,
                "quantity": quantity,
                "timestamp": pd.Timestamp.now()
            })
            db.commit()

        return {"status": "Inventory data uploaded successfully"}
    except Exception as e:
        logger.error(f"Error in upload_inventory_data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Endpoint to create an inventory item
@router.post("/create/", response_model=InventorySchema)
async def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter_by(product_code=inventory.product_code).first()
    if not product:
        raise HTTPException(status_code=400, detail="Product not found.")

    warehouse = db.query(Warehouse).filter_by(warehouse_code=inventory.warehouse_code).first()
    if not warehouse:
        raise HTTPException(status_code=400, detail="Warehouse not found.")

    db_inventory = Inventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

# Endpoint to get paginated and searchable inventories
@router.get("/", response_model=PaginatedResponse[InventorySchema])
async def get_inventories(
        db: Session = Depends(get_db),
        search: Optional[str] = Query(None, description="Search term for inventory data"),
        page: int = Query(1, ge=1, description="Page number for pagination"),
        page_size: int = Query(50, ge=1, le=200, description="Number of items per page")
):
    try:
        offset = (page - 1) * page_size
        query = db.query(Inventory)
        if search:
            search = search.lower()
            query = query.filter(
                or_(
                    Inventory.inventory_code.ilike(f"%{search}%"),
                    Inventory.product_code.ilike(f"%{search}%"),
                    Inventory.warehouse_code.ilike(f"%{search}%"),
                    Inventory.quantity.ilike(f"%{search}%")
                )
            )

        total_count = query.count()
        inventories = query.offset(offset).limit(page_size).all()

        return {
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "data": inventories
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/warehouse/{warehouse_code}")
async def get_warehouse_inventory(warehouse_code: str, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.warehouse_code == warehouse_code).all()
    if not inventory:
        raise HTTPException(status_code=404, detail="No inventory found for this warehouse code")
    return {"inventory": inventory}  # Test raw response



# Endpoint to get a single inventory item
@router.get("/{inventory_code}", response_model=InventorySchema)
async def get_inventory(inventory_code: str, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter_by(inventory_code=inventory_code).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found.")
    return inventory


# Endpoint to delete an inventory item
@router.delete("/delete/{inventory_code}")
async def delete_inventory(inventory_code: str, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter_by(inventory_code=inventory_code).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found.")

    db.delete(inventory)
    db.commit()
    return {"status": "Inventory deleted successfully"}


# Endpoint to update an inventory item
@router.put("/update/{inventory_code}", response_model=InventorySchema)
async def update_inventory(inventory_code: str, inventory: InventoryCreate, db: Session = Depends(get_db)):
    db_inventory = db.query(Inventory).filter_by(inventory_code=inventory_code).first()
    if not db_inventory:
        raise HTTPException(status_code=404, detail="Inventory not found.")

    for key, value in inventory.dict().items():
        setattr(db_inventory, key, value)

    db.commit()
    db.refresh(db_inventory)
    return db_inventory
