from datetime import datetime

from pydantic import BaseModel
from typing import List, Generic, TypeVar, Optional

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    total_count: int
    page: int
    page_size: int
    data: List[T]


#------------------------------------------------------------------------------
class ProductBase(BaseModel):
    product_code: str
    product_name: str
    unit_price: float


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    class Config:
        orm_mode = True


#------------------------------------------------------------------------------
class RegionBase(BaseModel):
    region_code: str
    region_name: str


class RegionCreate(RegionBase):
    pass


class Region(RegionBase):
    class Config:
        orm_mode = True


#------------------------------------------------------------------------------
class CityBase(BaseModel):
    city_code: str
    city_name: str
    region_code: Optional[str]  #null olabilir!


class CityCreate(CityBase):
    pass


class City(CityBase):
    class Config:
        orm_mode = True


#------------------------------------------------------------------------------

class WarehouseBase(BaseModel):
    warehouse_code: str
    warehouse_name: str
    city_code: str


class WarehouseCreate(WarehouseBase):
    pass


class Warehouse(WarehouseBase):
    class Config:
        orm_mode = True


#------------------------------------------------------------------------------
class InventoryBase(BaseModel):
    inventory_code: str
    product_code: str
    warehouse_code: str
    quantity: int
    timestamp: datetime  # Use ISO format for timestamps


class InventoryCreate(InventoryBase):
    pass


class Inventory(InventoryBase):
    class Config:
        orm_mode = True


#------------------------------------------------------------------------------
class YearlyAverageConsumptionBase(BaseModel):
    product_code: str
    average_usage: Optional[float]
    year: int


class YearlyAverageConsumptionCreate(YearlyAverageConsumptionBase):
    pass


class YearlyAverageConsumption(YearlyAverageConsumptionBase):
    id: int

    class Config:
        orm_mode = True
