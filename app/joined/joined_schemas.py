from pydantic import BaseModel
from datetime import datetime

class JoinedInventoryResponse(BaseModel):
    inventory_code: str
    product_code: str
    product_name: str
    warehouse_code: str
    warehouse_name: str
    quantity: int
    timestamp: datetime

    class Config:
        orm_mode = True
