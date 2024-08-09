from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Region, City, Warehouse, Product, Inventory, WeeklyData, RequestPoint

DATABASE_URL = "mysql+pymysql://zaywreck:Zaywreck6378.@localhost/warehouse_management"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Drop all tables in the correct order
Base.metadata.drop_all(bind=engine, tables=[Inventory.__table__, WeeklyData.__table__, RequestPoint.__table__, Warehouse.__table__, City.__table__, Region.__table__, Product.__table__])

# Create tables
Base.metadata.create_all(bind=engine)

# Insert initial data
def insert_initial_data(session):
    # Regions
    marmara = Region(region_name="Marmara", region_code="MAR")
    anadolu = Region(region_name="Anadolu", region_code="ANA")
    session.add(marmara)
    session.add(anadolu)
    session.commit()

    # Cities
    istanbul = City(city_name="Istanbul", city_code="34", region_code=marmara.region_code)
    ankara = City(city_name="Ankara", city_code="06", region_code=anadolu.region_code)
    session.add(istanbul)
    session.add(ankara)
    session.commit()

    # Warehouses
    warehouse1 = Warehouse(warehouse_name="Warehouse1", warehouse_code="34YB", city_code=istanbul.city_code)
    warehouse2 = Warehouse(warehouse_name="Warehouse2", warehouse_code="06XB", city_code=ankara.city_code)
    session.add(warehouse1)
    session.add(warehouse2)
    session.commit()

    # Products
    product1 = Product(product_code="M001", product_name="Product1", unit_price=10.0)
    product2 = Product(product_code="M002", product_name="Product2", unit_price=20.0)
    session.add(product1)
    session.add(product2)
    session.commit()

session = SessionLocal()
insert_initial_data(session)
session.close()