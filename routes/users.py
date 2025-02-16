
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth import get_current_admin, hash_password, verify_password, create_access_token, get_current_user
from database import get_db
from models import User
from schemas import UserSchema


users_router = APIRouter(
    prefix='/profile',
    tags=["Users"]    
)


# login, singup

@users_router.post("/signup", response_model=UserSchema, response_model_exclude={
    "user_id", "role", "password"
})
async def signup_user(user : UserSchema, db: AsyncSession = Depends(get_db)):
    new_user = User(
        user_id = user.user_id,
        username=user.username,
        email = user.email,
        password = hash_password(user.password),
        is_active = user.is_active,
        role = user.role
    )
    result = await db.execute(select(User).where(User.username == user.username))
    user = result.scalars().first()

    if user:
        raise HTTPException(
            status_code=400,
            detail="username is already exist"
        )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@users_router.post("/login")
async def login(user : dict, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user["username"]))
    existing_user = result.scalars().first()
    if not existing_user or not verify_password(user["password"], existing_user.password):
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    access_token = create_access_token(data={"sub": existing_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# user
@users_router.get("/admin")
async def get_all_users(
        admin_user: dict = Depends(get_current_admin), db: AsyncSession = Depends(get_db)
):
    results = await db.execute(select(User).options(selectinload(User.orders)))
    users = results.scalars().all(),

    return users

@users_router.get("/")
async def get_current_user(user : dict =Depends(get_current_user)):
    return user

@users_router.patch("/")
async def put_profile(
        update_user: dict,
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter(User.username == current_user.username))
    existing_user = result.scalars().first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="Its not your profile.")

    for key, value in update_user.items():
        if value:
            setattr(existing_user, key, value)

    await db.commit()
    await db.refresh(existing_user)

    return {"message": "Profile updated successfully", "username": existing_user.username}

@users_router.delete("/{username}")
async def delete_profile(username : str, admin_user : dict = Depends(get_current_admin), db: AsyncSession= Depends(get_db)):
    user = await db.execute(select(User).where(User.username == username))
    user = user.scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail = "User not found"
        )

    await db.delete(user)
    await db.commit()

    return {"msg":"User delete"}