from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Region
from app.schemas import Region as RegionSchema, RegionCreate

router = APIRouter()

@router.get("/", response_model=List[RegionSchema])
async def get_all_regions(db: Session = Depends(get_db)):
    regions = db.query(Region).all()
    return regions

@router.get("/{region_code}", response_model=RegionSchema)
async def get_region(region_code: str, db: Session = Depends(get_db)):
    region = db.query(Region).filter_by(region_code=region_code).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found.")
    return region

@router.post("/", response_model=RegionSchema)
async def create_region(region: RegionCreate, db: Session = Depends(get_db)):
    existing_region = db.query(Region).filter_by(region_code=region.region_code).first()
    if existing_region:
        raise HTTPException(status_code=400, detail="Region already exists.")

    db_region = Region(**region.dict())
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region

@router.put("/{region_code}", response_model=RegionSchema)
async def update_region(region_code: str, region: RegionCreate, db: Session = Depends(get_db)):
    db_region = db.query(Region).filter(Region.region_code == region_code).first()
    if not db_region:
        raise HTTPException(status_code=404, detail="Region not found")

    for key, value in region.dict().items():
        setattr(db_region, key, value)

    db.commit()
    db.refresh(db_region)
    return db_region

@router.delete("/{region_code}", response_model=dict)
async def delete_region(region_code: str, db: Session = Depends(get_db)):
    region = db.query(Region).filter_by(region_code=region_code).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found.")

    db.delete(region)
    db.commit()
    return {"status": "Region deleted successfully"}
