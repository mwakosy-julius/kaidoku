from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import requests

from core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)
from app.db.database import get_db
from app.db.models import User
from app.models.user import Token, UserCreate, User as UserSchema

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserSchema)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, email=str(user.email), hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserSchema)
def read_users_me(current_user=Depends(get_current_active_user)):
    return current_user


@router.get("/users/tools")
def get_tools(current_user=Depends(get_current_active_user)):
    tools = [
        {"name": "Pairwise Alignment", "url": "/pairwise_alignment/"},
        {"name": "Multiple Sequence Alignment", "url": "/multiple_alignment/"},
        {"name": "GC Content Calculator", "url": "/gc_content/"},
        {"name": "Codon Usage Calculator", "url": "/codon_usage/"},
        {"name": "DNA Visualization Tool", "url": "/dna_visualization/"},
        {"name": "MusicDNA", "url": "/musicdna/"},
        {"name": "Blast", "url": "/blast/"},
        {"name": "Phylogenetic Tree", "url": "/phylogenetic_tree/"},
    ]
    return {"tools": tools}


@router.post("/google", response_model=Token)
async def google_login(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    # 1. Verify token with Google
    google_response = requests.get(
        f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
    )
    if google_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    google_data = google_response.json()
    email = google_data["email"]
    username = google_data.get("name", email.split("@")[0])

    # 2. Find or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(username=username, email=email, hashed_password="", is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)

    # 3. Issue your app's JWT
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
