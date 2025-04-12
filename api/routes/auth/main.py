from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user,
    create_access_token,
    verify_password,
)
from models.user import User, Token, UserCreate
from api.routes.auth.user_crud import (
    get_user_by_username,
    get_user_by_email,
    create_user,
)

router = APIRouter(prefix="/auth")


async def authenticate_user(username: str, password: str):
    """Authenticate a user by username and password"""
    user = await get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


@router.post("/signup", response_model=User)
async def signup(user: UserCreate):
    """Register a new user"""
    existing_user = await get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    existing_email = await get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    db_user = await create_user(user)
    return db_user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Generate access token for authenticated user"""
    user = await authenticate_user(form_data.username, form_data.password)
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


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user"""
    return current_user


@router.get("/users/tools")
async def get_tools(current_user: User = Depends(get_current_active_user)):
    """Get tools available to authenticated user"""
    tools = [
        {"name": "Pairwise Alignment", "url": "/pairwise_alignment/"},
        {"name": "Multiple Sequence Alignment", "url": "/multiple_alignment/"},
        {"name": "GC Content Calculator", "url": "/gc_content/"},
        {"name": "Codon Usage Calculator", "url": "/codon_usage/"},
        {"name": "DNA Visualization Tool", "url": "/dna_visualization/"},
        {"name": "MusicDNA", "url": "/musicdna/"},
        {"name": "Blast", "url": "/blast/"},
        {"name": "Phylogenetic Tree", "url": "/phylogenetic_tree/"},
        {"name": "Variant Calling", "url": "/variant_calling/"},
        {"name": "Motif Finder", "url": "/motif_finder/"},
        {"name": "Consensus Maker", "url": "/consensus_maker/"},
        {"name": "Data Compression", "url": "/data_compression/"},
    ]
    return {"tools": tools}
