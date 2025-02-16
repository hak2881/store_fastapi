from datetime import datetime
import uuid
from typing import List

from pydantic import computed_field
from sqlalchemy import Column, String, Boolean, Integer, DECIMAL, DATETIME, Float, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default = "user")
    is_active = Column(Boolean)

    # 첫번째인자: 연결할 모델 클래스명, 유저에서 찾는거니까,
    # 생성시에 역참조할거는 아직 DB에 없으니까 함수내에서 찾아야함 그래서 클래스명 자체를 쓰는거임 Order
    # sql 에선 실재로 이런관계가 없으니 sqlalchemy 자체에서 찾아야함 그래서 클래스명으로 사용
    # 두번째인자: Order테이블의 user를 참조한것
    # relationship()은 ForeignKey()와 다르게 SQLAlchemy ORM 내부에서 참조할 필드명을 사용해야 하기 때문에 user를 써야 함
    orders = relationship("Order", back_populates="user", cascade="all, delete")

order_products = Table(
    "order_products",
    Base.metadata,
    Column("order_id", ForeignKey("orders.order_id"), primary_key=True),
    Column("product_id", ForeignKey("products.product_id"), primary_key=True)
)

class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    total_price = Column(DECIMAL(65, 2))
    is_paid = Column(Boolean)
    created_at = Column(DATETIME, default=datetime.utcnow)


    # 실제 users의 DB테이블 이름을 가르킴, 이건 SQL내에서 실행되야 하는거니까

    username = Column(ForeignKey('users.username'),nullable=False)
    user = relationship("User", back_populates="orders")

    # Product 과 참조
    products = relationship("Product", secondary=order_products, back_populates="orders")


class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    discount = Column(Float)
    final_price = Column(Float)

    # Order와 참조
    orders = relationship("Order", secondary=order_products, back_populates="products")






