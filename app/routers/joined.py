from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.default.models import Inventory, Warehouse, Product, YearlyAverageConsumption
from app.joined.joined_schemas import JoinedInventoryResponse

router = APIRouter()

@router.get("/inventory", response_model=List[JoinedInventoryResponse])
async def get_joined_inventory(warehouse_code: str, db: Session = Depends(get_db)):
    try:
        query = (
            db.query(
                Inventory.inventory_code,
                Inventory.product_code,
                Inventory.warehouse_code,
                Inventory.quantity,
                Inventory.timestamp,
                Warehouse.warehouse_name,
                Product.product_name,
                YearlyAverageConsumption.average_usage
            )
            .join(Warehouse, Inventory.warehouse_code == Warehouse.warehouse_code)
            .join(Product, Inventory.product_code == Product.product_code)
            .outerjoin(YearlyAverageConsumption, Inventory.product_code == YearlyAverageConsumption.product_code)
            .filter(Inventory.warehouse_code == warehouse_code)
            .all()
        )

        if not query:
            raise HTTPException(status_code=404, detail="No inventory data found for the given warehouse")

        results = [
            {
                "inventory_code": inv_code,
                "product_code": prod_code,""
                "warehouse_code": wh_code,
                "quantity": quantity,
                "timestamp": timestamp.isoformat(),
                "warehouse_name": wh_name,
                "product_name": prod_name,
                "average_consumption": avg_usage
            }
            for inv_code, prod_code, wh_code, quantity, timestamp, wh_name, prod_name, avg_usage in query
        ]

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
