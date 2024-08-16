from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.default.models import Warehouse, Inventory
from app.default.schemas import Warehouse as WarehouseSchema, WarehouseCreate

router = APIRouter()

class WarehouseResponse(WarehouseSchema):
    class Config:
        orm_mode = True

@router.get("/", response_model=List[WarehouseResponse])
async def get_all_warehouses(db: Session = Depends(get_db)):
    return db.query(Warehouse).all()

@router.get("/{warehouse_code}", response_model=WarehouseResponse)
async def get_warehouse_data(warehouse_code: str, db: Session = Depends(get_db)):
    warehouse = db.query(Warehouse).filter_by(warehouse_code=warehouse_code).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse

@router.post("/", response_model=WarehouseResponse)
async def create_warehouse(warehouse: WarehouseCreate, db: Session = Depends(get_db)):
    db_warehouse = Warehouse(**warehouse.dict())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse

@router.put("/update/{warehouse_code}", response_model=WarehouseResponse)
async def update_warehouse(warehouse_code: str, warehouse: WarehouseCreate, db: Session = Depends(get_db)):
    # Convert to string if necessary
    warehouse_code = str(warehouse_code)

    # Query to find the warehouse by code
    db_warehouse = db.query(Warehouse).filter(Warehouse.warehouse_code == warehouse_code).first()

    # Check if the warehouse exists
    if not db_warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    # Update the warehouse attributes
    for key, value in warehouse.dict().items():
        setattr(db_warehouse, key, value)

    # Commit changes to the database
    db.commit()
    db.refresh(db_warehouse)

    return db_warehouse


@router.delete("/{warehouse_code}", response_model=dict)
async def delete_warehouse(warehouse_code: str, db: Session = Depends(get_db)):
    # First delete related inventory records
    db.query(Inventory).filter(Inventory.warehouse_code == warehouse_code).delete(synchronize_session=False)

    # Then delete the warehouse
    warehouse = db.query(Warehouse).filter_by(warehouse_code=warehouse_code).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    db.delete(warehouse)
    db.commit()
    return {"message": "Warehouse deleted successfully"}



