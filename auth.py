from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from sqlalchemy.orm import Session

from app.core.security import (
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

GOOGLE_CLIENT_ID = "133426663689-2i05ddo0v7kcqikp29cgka2h1ob25cc8.apps.googleusercontent.com"


class GoogleCredential(BaseModel):
    credential: str


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


@router.post("/auth/google")
async def google_login(data: GoogleCredential):
    try:
        # Verify Google ID token
        idinfo = id_token.verify_oauth2_token(
            data.credential,
            grequests.Request(),
            GOOGLE_CLIENT_ID,
        )
        email = idinfo["email"]
        name = idinfo.get("name")
        picture = idinfo.get("picture")

        # Find or create user
        user = await User.find_one({"email": email})
        if not user:
            user = await User.create(
                {
                    "email": email,
                    "name": name,
                    "avatar": picture,
                    "login_type": "google",
                }
            )

        # Generate your own JWT
        token = create_access_token(user.id)

        return {
            "token": token,
            "user": {"email": user.email, "name": user.name, "avatar": user.avatar},
        }
    except Exception as e:
        print("Google login error:", e)
        raise HTTPException(status_code=401, detail="Google login failed")