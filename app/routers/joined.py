from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Inventory, Warehouse, Product
from app.schemas import Inventory as InventorySchema

router = APIRouter()


class JoinedInventoryResponse(InventorySchema):
    warehouse_name: str
    product_name: str

    class Config:
        orm_mode = True


@router.get("/inventory", response_model=List[JoinedInventoryResponse])
async def get_joined_inventory(warehouse_code: str, db: Session = Depends(get_db)):
    # Perform the join query
    try:
        query = (
            db.query(Inventory, Warehouse.warehouse_name, Product.product_name)
            .join(Warehouse, Inventory.warehouse_code == Warehouse.warehouse_code)
            .join(Product, Inventory.product_code == Product.product_code)
            .filter(Inventory.warehouse_code == warehouse_code)
            .all()
        )

        if not query:
            raise HTTPException(status_code=404, detail="No inventory data found for the given warehouse")

        # Transform results to fit the schema
        results = [
            {
                "inventory_code": inv.inventory_code,
                "product_code": inv.product_code,
                "warehouse_code": inv.warehouse_code,
                "quantity": inv.quantity,
                "timestamp": inv.timestamp.isoformat(),
                "warehouse_name": warehouse_name,
                "product_name": product_name,
            }
            for inv, warehouse_name, product_name in query
        ]

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
