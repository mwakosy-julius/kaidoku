from datetime import timedelta, datetime
from core.config import settings
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from models.user import UserLogin

from core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    get_current_active_user,
    create_access_token,
    verify_password,
    get_user_from_refresh_token,
    create_refresh_token,
    store_refresh_token,
)
from models.user import User, Token, UserCreate
from api.routes.auth.user_crud import (
    get_user_by_username,
    get_user_by_email,
    create_user,
    invalidate_refresh_token,
)

router = APIRouter(prefix="/auth")


async def authenticate_user(email: str, password: str):
    """Authenticate a user by username and password"""
    user = await get_user_by_email(email)
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
async def login_for_access_token(response: Response, form_data: UserLogin):
    """Generate access token for authenticated user and set refresh token cookie"""
    user = await authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(user.id)

    token_id = user.id
    await store_refresh_token(
        user.id, token_id, datetime.utcnow() + refresh_token_expires
    )

    # Set refresh token as HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,  # True in production
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # in seconds
        path="/auth",  # Restrict to auth endpoints
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
        {
            "name": "Pairwise Alignment",
            "description": "Compare two sequences to find similarities and differences",
            "url": "/api/tools/pairwise_alignment",
            "frontend_url": "/pairwise_alignment",
        },
        {
            "name": "Multiple Sequence Alignment",
            "description": "Align three or more biological sequences for comparative analysis",
            "url": "/api/tools/multiple_alignment",
            "frontend_url": "/multiple_alignment",
        },
        {
            "name": "GC Content Calculator",
            "description": "Calculate the percentage of G and C bases in DNA sequences",
            "url": "/api/tools/gc_content",
            "frontend_url": "/gc_content",
        },
        {
            "name": "Codon Usage Calculator",
            "description": "Analyze codon frequency and bias in coding sequences",
            "url": "/api/tools/codon_usage",
            "frontend_url": "/codon_usage",
        },
        {
            "name": "DNA Visualization Tool",
            "description": "Generate visual representations of DNA sequences",
            "url": "/api/tools/dna_visualization",
            "frontend_url": "/dna_visualization",
        },
        {
            "name": "MusicDNA",
            "description": "Convert DNA sequences into musical patterns and melodies",
            "url": "/api/tools/musicdna",
            "frontend_url": "/music_dna",
        },
        {
            "name": "Blast",
            "description": "Find regions of similarity between biological sequences",
            "url": "/api/tools/blast",
            "frontend_url": "/blast",
        },
        {
            "name": "Phylogenetic Tree",
            "description": "Generate evolutionary trees from sequence data",
            "url": "/api/tools/phylogenetic_tree",
            "frontend_url": "/phylogenetic_tree",
        },
        {
            "name": "Variant Calling",
            "description": "Identify variants in sequencing data compared to a reference",
            "url": "/api/tools/variant_calling",
            "frontend_url": "/variant_calling",
        },
        {
            "name": "Motif Finder",
            "description": "Discover recurring patterns in biological sequences",
            "url": "/api/tools/motif_finder",
            "frontend_url": "/motif_finder",
        },
        {
            "name": "Consensus Maker",
            "description": "Generate consensus sequences from multiple alignments",
            "url": "/api/tools/consensus_maker",
            "frontend_url": "/consensus_maker",
        },
        {
            "name": "Data Compression",
            "description": "Compress genomic data for efficient storage and transfer",
            "url": "/api/tools/data_compression",
            "frontend_url": "/data_compression",
        },
        {
            "name": "Metagenomics",
            "description": "Analyze genetic material from environmental samples",
            "url": "/api/tools/metagenomics",
            "frontend_url": "/metagenomics",
        },
    ]
    return tools


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str = Cookie(None)):
    """Generate a new access token using a refresh token"""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_from_refresh_token(refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user),
    refresh_token: str = Cookie(None),
):
    """Logout user by invalidating refresh token"""
    # Invalidate the refresh token in the database
    if refresh_token:
        await invalidate_refresh_token(refresh_token)

    # Clear the cookies
    response.delete_cookie(key="refresh_token")

    return {"message": "Successfully logged out"}
