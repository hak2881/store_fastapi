from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="profile/login")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt

async def get_current_user(token : str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
        
        username = payload.get("sub")
        exp = payload.get("exp")
        
        if username is None:
            raise HTTPException(status_code=401, detail = "Invalid token")

        result = await db.execute(
            select(User)
            .options(selectinload(User.orders))
            .where(User.username==username)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        if exp is None or datetime.now() > datetime.fromtimestamp(exp):
            raise HTTPException(status_code=401, detail="Token has expired")
        
        return user
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail= "Access denied. Admins only")
     
    return user