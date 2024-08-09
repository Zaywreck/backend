from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import City

router = APIRouter()

@router.get("/")
async def get_all_cities(db: Session = Depends(get_db)):
    cities = db.query(City).all()
    return [{"city_code": c.city_code, "city_name": c.city_name} for c in cities]
