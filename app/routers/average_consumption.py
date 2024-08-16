from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.default.models import YearlyAverageConsumption
from app.default.schemas import YearlyAverageConsumption as YearlyAverageConsumptionSchema, \
    YearlyAverageConsumptionCreate

router = APIRouter()


@router.get("/", response_model=List[YearlyAverageConsumptionSchema])
async def get_all_yearly_average_consumptions(db: Session = Depends(get_db)):
    averages = db.query(YearlyAverageConsumption).all()
    return averages


@router.get("/{id}", response_model=YearlyAverageConsumptionSchema)
async def get_yearly_average_consumption(id: int, db: Session = Depends(get_db)):
    average = db.query(YearlyAverageConsumption).filter_by(id = id).first()
    if not average:
        raise HTTPException(status_code=404, detail="Yearly Average Consumption not found.")
    return average


@router.post("/create/", response_model=YearlyAverageConsumptionSchema)
async def create_yearly_average_consumption(average: YearlyAverageConsumptionCreate, db: Session = Depends(get_db)):
    existing_average = db.query(YearlyAverageConsumption).filter_by(product_code=average.product_code,
                                                                    year=average.year).first()
    if existing_average:
        raise HTTPException(status_code=400,
                            detail="Yearly Average Consumption already exists for this product and year.")

    db_average = YearlyAverageConsumption(**average.dict())
    db.add(db_average)
    db.commit()
    db.refresh(db_average)
    return db_average


@router.put("/update/{id}", response_model=YearlyAverageConsumptionSchema)
async def update_yearly_average_consumption(id: int, average: YearlyAverageConsumptionCreate,
                                            db: Session = Depends(get_db)):
    db_average = db.query(YearlyAverageConsumption).filter(YearlyAverageConsumption.id == id).first()
    if not db_average:
        raise HTTPException(status_code=404, detail="Yearly Average Consumption not found")

    for key, value in average.dict().items():
        setattr(db_average, key, value)

    db.commit()
    db.refresh(db_average)
    return db_average


@router.delete("/delete/{id}")
async def delete_yearly_average_consumption(id: int, db: Session = Depends(get_db)):
    average = db.query(YearlyAverageConsumption).filter_by(id=id).first()
    if not average:
        raise HTTPException(status_code=404, detail="Yearly Average Consumption not found.")

    db.delete(average)
    db.commit()
    return {"status": "Yearly Average Consumption deleted successfully"}
