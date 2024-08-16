from typing import Optional
from app.default.schemas import InventoryBase

class JoinedInventoryResponse(InventoryBase):
    product_name: str
    warehouse_name: str
    average_consumption: Optional[float]  # Should be Optional in case no average is found

    class Config:
        orm_mode = True
