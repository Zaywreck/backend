from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, warehouses, cities, inventory, regions, auth,joined, average_consumption

app = FastAPI()

# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(warehouses.router, prefix="/warehouses", tags=["Warehouses"])
app.include_router(cities.router, prefix="/cities", tags=["Cities"])
app.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
app.include_router(regions.router, prefix="/regions", tags=["Regions"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(joined.router, prefix="/joined", tags=["joined"])
app.include_router(average_consumption.router, prefix="/average", tags=["average"])
