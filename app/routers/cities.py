from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.default.models import City
from app.default.schemas import City as CitySchema, CityCreate

router = APIRouter()

@router.get("/", response_model=List[CitySchema])
async def get_all_cities(db: Session = Depends(get_db)):
    cities = db.query(City).all()
    return cities

@router.get("/{city_code}", response_model=CitySchema)
async def get_city(city_code: str, db: Session = Depends(get_db)):
    city = db.query(City).filter_by(city_code=city_code).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found.")
    return city

@router.post("/create/", response_model=CitySchema)
async def create_city(city: CityCreate, db: Session = Depends(get_db)):
    existing_city = db.query(City).filter_by(city_code=city.city_code).first()
    if existing_city:
        raise HTTPException(status_code=400, detail="City already exists.")

    db_city = City(**city.dict())
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city

@router.put("/update/{city_code}", response_model=CitySchema)
async def update_city(city_code: str, city: CityCreate, db: Session = Depends(get_db)):
    db_city = db.query(City).filter(City.city_code == city_code).first()
    if not db_city:
        raise HTTPException(status_code=404, detail="City not found")

    for key, value in city.dict().items():
        setattr(db_city, key, value)

    db.commit()
    db.refresh(db_city)
    return db_city

@router.delete("/delete/{city_code}")
async def delete_city(city_code: str, db: Session = Depends(get_db)):
    city = db.query(City).filter_by(city_code=city_code).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found.")

    db.delete(city)
    db.commit()
    return {"status": "City deleted successfully"}
