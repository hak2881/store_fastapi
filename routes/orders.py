from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth import get_current_admin, get_current_user
from database import get_db
from models import Order, Product
from schemas import OrderSchema

orders_router = APIRouter(
    prefix="/orders",
    tags = ["Order"]
)


@orders_router.get("/admin")
async def get_all_orders(db: AsyncSession = Depends(get_db), admin : dict = Depends(get_current_admin)):
    results = await db.execute(select(Order).options(selectinload(Order.products)))
    orders = results.scalars().all()

    return orders

@orders_router.post("/")
async def create_order(
        order: OrderSchema,
        db: AsyncSession=Depends(get_db),
        user : dict = Depends(get_current_user)
    ):
    products = await db.execute(select(Product).where(Product.product_id.in_(order.products)))
    products = products.scalars().all()

    if not products:
        raise HTTPException(status_code=400, detail="No valid products found")

    new_order = Order(
        username = user.username,
        total_price = order.total_price,
        is_paid = order.is_paid,
        products = products
    )

    # db.add(new_order)
    # await db.commit()
    # await db.refresh(new_order)
    # # 주문이 없는 관계에서 바로 추가하면 주문이 없는 상태이기에 에러가 발생 그래서 따로 생성해야함
    # # Many-to-Many 관계(relationship(secondary=order_products))에서 .extend()를 호출하면,
    # # SQLAlchemy ORM이 내부적으로 변경을 감지하고 트랜잭션에 포함함
    # # 이 트랜잭션을 DB에 반영하려면 반드시 db.commit()을 호출해야 함
    # new_order.products.extend(products)
    # await db.commit()
    # await db.refresh(new_order)
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    return new_order

    return new_order


@orders_router.get(
    "/",
    response_model=List[OrderSchema],
    response_model_exclude={
        "order_id",
        "is_paid",
        "created_at"
    }
)
async def current_user_orders(db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    orders = await db.execute(
        select(Order)
        .options(selectinload(Order.products))
        .where(Order.username == user.username)
    )
    orders = orders.scalars().all()

    orders_with_products =[
        {
            "username": order.username,
            "total_price": order.total_price,
            "is_paid": order.is_paid,
            "created_at": order.created_at,
            "product_id": [product.product_id for product in order.products]
        }
        for order in orders
    ]

    return orders_with_products

@orders_router.delete("/{order_id}")
async def delete_order(order_id : int, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    order = await db.execute(select(Order).where(Order.order_id == order_id))
    order = order.scalars().first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="order not found"
        )
    if order.username != user.username:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this order"
        )

    await db.delete(order)
    await db.commit()
    return {"msg" : "Success delete"}