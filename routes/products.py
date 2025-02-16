from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_admin
from database import get_db
from models import Product
from schemas import ProductSchema



products_router = APIRouter(
    prefix="/products",
    tags=["products"]
)

# products
@products_router.post("/")
async def create_product(product: ProductSchema, db: AsyncSession=Depends(get_db), admin : dict = Depends(get_current_admin)):
    new_product = Product(
        name = product.name,
        price = product.price,
        discount = product.discount,
        final_price= product.final_price,
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@products_router.get("/")
async def get_products(db: AsyncSession=Depends(get_db), admin : dict = Depends(get_current_admin)):
    results = await db.execute(select(Product))
    products = results.scalars().all()
    return products

@products_router.patch("/{product_id}")
async def patch_product(product_id: int ,update_product :ProductSchema, db: AsyncSession=Depends(get_db), admin : dict = Depends(get_current_admin)):
    result = await db.execute(select(Product).where(Product.product_id == product_id))
    product = result.scalars().first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    for key, value in update_product.items():
        if value:
            setattr(product, key, value)
    if update_product.get("price") is not None or update_product.get("discount") is not None:
        product.final_price = product.price * (1 - (product.discount or 0) / 100)
    await db.commit()
    await db.refresh(product)
    return product

@products_router.delete("/{product_id}")
async def delete_product(product_id: int, db: AsyncSession=Depends(get_db), admin : dict = Depends(get_current_admin)):
    result = await db.execute(select(Product).where(Product.product_id == product_id))
    product = result.scalars().first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    await db.delete(product)
    await db.commit()

    return {"msg": "Product deleted"}


