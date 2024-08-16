from sqlalchemy import Column, String, Float, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    product_code = Column(String(50), primary_key=True, index=True)
    product_name = Column(String(100))
    unit_price = Column(Float)

class Region(Base):
    __tablename__ = 'regions'
    region_code = Column(String(50), primary_key=True, index=True)
    region_name = Column(String(100))
    cities = relationship("City", back_populates="region")
class City(Base):
    __tablename__ = 'cities'
    city_code = Column(String(50), primary_key=True, index=True)
    city_name = Column(String(100))
    region_code = Column(String(50), ForeignKey('regions.region_code'))
    region = relationship("Region", back_populates="cities")
    warehouses = relationship("Warehouse", back_populates="city")


class Warehouse(Base):
    __tablename__ = 'warehouses'
    warehouse_code = Column(String, primary_key=True)
    warehouse_name = Column(String)
    city_code = Column(String, ForeignKey('cities.city_code'))

    city = relationship("City", back_populates="warehouses")
    inventory = relationship("Inventory", back_populates="warehouse", cascade="all, delete-orphan")

class Inventory(Base):
    __tablename__ = 'inventory'
    inventory_code = Column(String, primary_key=True)
    product_code = Column(String, ForeignKey('products.product_code'))
    warehouse_code = Column(String, ForeignKey('warehouses.warehouse_code'))
    quantity = Column(Integer)
    timestamp = Column(TIMESTAMP)

    warehouse = relationship("Warehouse", back_populates="inventory")

class YearlyAverageConsumption(Base):
    __tablename__ = 'yearly_average_consumption'
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), ForeignKey('products.product_code'))
    average_usage = Column(Float)
    year = Column(Integer)  # Store the year for which the average is applicable

    product = relationship("Product")
