from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

from app import auth_model
from app.auth import auth_schema
from app.database import get_db
from app.utils.security import verify_api_key

router = APIRouter()
SECRET_KEY = "7c7f55abb883c3d4b16f69a15e0c29fc"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=auth_schema.UserResponse)
def register(user: auth_schema.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if the email is already registered
        db_user = db.query(auth_model.User).filter(auth_model.User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the password
        hashed_password = pwd_context.hash(user.password)

        # Create new user
        db_user = auth_model.User(username=user.username, hashed_password=hashed_password, email=user.email)
        db.add(db_user)
        db.commit()

        # Fetch the default role
        default_role = db.query(auth_model.Role).filter(auth_model.Role.name == "user").first()
        if default_role:
            db_user.roles.append(default_role)
            db.commit()

        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=auth_schema.Token)
def login(user: auth_schema.UserCreate, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)):
    print(f"Received user data: {user}")
    print(f"API Key: {api_key}")

    # Check if user exists by email
    db_user = db.query(auth_model.User).filter(auth_model.User.email == user.email).first()
    print(f"Database user: {db_user}")

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email")

    if not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    print(f"Generated access token: {access_token}")

    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        db_user = db.query(auth_model.User).filter(auth_model.User.email == email).first()
        if db_user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return db_user

def verify_api_key(api_key: str = Header(...)):
    if api_key != SECRET_KEY:  # Replace with your actual API key
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

@router.get("/me", response_model=auth_schema.UserResponse)
def get_current_user_info(current_user: auth_model.User = Depends(get_current_user)):
    print("auth check: "+ str(datetime.now()))
    return current_user

@router.post("/logout")
def logout():
    return {"message": "Successfully logged out"}
