from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from jose import jwt

from api.routes.auth.user_crud import (
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from core.config import settings
from core.db import db
from core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    cleanup_expired_tokens,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_password_hash,
    get_user_from_refresh_token,
    invalidate_refresh_token,
    revoke_all_user_tokens,
    rotate_refresh_token,
    store_refresh_token,
    verify_password,
)
from models.user import Token, User, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


async def authenticate_user(email: str, password: str) -> Optional[UserResponse]:
    """Authenticate a user by email and password"""
    try:
        user_in_db = await get_user_by_email(email)
        if not user_in_db:
            return None

        if not verify_password(password, user_in_db.password):
            return None

        # Return User model (without password)
        return UserResponse(
            _id=user_in_db.id,
            username=user_in_db.username,
            email=user_in_db.email,
            is_active=user_in_db.is_active,
            created_at=user_in_db.created_at,
        )
    except Exception as e:
        print(f"Authentication error: {e}")
        return None


@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if username already exists
        existing_user = await get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered",
            )

        # Check if email already exists
        existing_email = await get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        # Hash password before storing
        hashed_password = get_password_hash(user_data.password)
        user_data.password = hashed_password

        # Create user in database
        db_user = await create_user(user_data)

        # Return User model (without password)
        return User(
            _id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            password=db.password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(response: Response, form_data: UserLogin):
    """Generate access token for authenticated user and set refresh token cookie"""
    try:
        # Authenticate user
        user = await authenticate_user(form_data.email, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
            )

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        # Create refresh token
        refresh_token = create_refresh_token(str(user.id))

        # Decode refresh token to get JTI for database storage
        refresh_payload: Dict[str, Any] = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        token_id = refresh_payload.get("jti")
        refresh_expires = datetime.fromtimestamp(refresh_payload.get("exp"))

        # Store refresh token in database
        await store_refresh_token(str(user.id), token_id, refresh_expires)

        # Set refresh token as HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=False,
            secure=settings.COOKIE_SECURE,  # True in production
            samesite="lax",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # Fixed calculation
            path="/auth",  # Restrict to auth endpoints
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    response: Response,
    refresh_token: str = Cookie(None),
    rotate_token: bool = False,  # Optional token rotation
):
    """Generate a new access token using a refresh token"""
    try:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate refresh token and get user
        user = await get_user_from_refresh_token(refresh_token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is still active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
            )

        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        # Optional: Rotate refresh token for enhanced security
        if rotate_token:
            new_refresh_token = await rotate_refresh_token(refresh_token, str(user.id))
            if new_refresh_token:
                response.set_cookie(
                    key="refresh_token",
                    value=new_refresh_token,
                    httponly=True,
                    secure=settings.COOKIE_SECURE,
                    samesite="lax",
                    max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
                    path="/auth",
                )

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user),
    refresh_token: str = Cookie(None),
):
    """Logout user by invalidating refresh token"""
    try:
        # Invalidate the refresh token in the database
        if refresh_token:
            await invalidate_refresh_token(refresh_token)

        # Clear the refresh token cookie
        response.delete_cookie(key="refresh_token", path="/auth")

        return {"message": "Successfully logged out"}

    except Exception as e:
        print(f"Logout error: {e}")
        # Still return success even if token invalidation fails
        response.delete_cookie(key="refresh_token", path="/auth")
        return {"message": "Logged out"}


@router.post("/logout-all")
async def logout_all_devices(
    response: Response,
    current_user: User = Depends(get_current_active_user),
    refresh_token: str = Cookie(None),
):
    """Logout user from all devices by revoking all refresh tokens"""
    try:
        # Revoke all refresh tokens for this user
        await revoke_all_user_tokens(str(current_user.id))

        # Clear the current refresh token cookie
        response.delete_cookie(key="refresh_token", path="/auth")

        return {"message": "Successfully logged out from all devices"}

    except Exception as e:
        print(f"Logout all error: {e}")
        # Still clear cookie even if database operation fails
        response.delete_cookie(key="refresh_token", path="/auth")
        return {"message": "Logged out from current device"}


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current authenticated user"""
    return current_user


@router.get("/users/tools")
async def get_tools(current_user: User = Depends(get_current_active_user)):
    """Get tools available to authenticated user"""
    tools = [
        {
            "id": "pairwise_alignment",
            "name": "Pairwise Alignment",
            "description": "Compare two sequences to find similarities and differences",
            "url": "/api/tools/pairwise_alignment",
            "frontend_url": "/pairwise_alignment",
            "category": "alignment",
        },
        {
            "id": "multiple_alignment",
            "name": "Multiple Sequence Alignment",
            "description": "Align three or more biological sequences for comparative analysis",
            "url": "/api/tools/multiple_alignment",
            "frontend_url": "/multiple_alignment",
            "category": "alignment",
        },
        {
            "id": "gc_content",
            "name": "GC Content Calculator",
            "description": "Calculate the percentage of G and C bases in DNA sequences",
            "url": "/api/tools/gc_content",
            "frontend_url": "/gc_content",
            "category": "analysis",
        },
        {
            "id": "codon_usage",
            "name": "Codon Usage Calculator",
            "description": "Analyze codon frequency and bias in coding sequences",
            "url": "/api/tools/codon_usage",
            "frontend_url": "/codon_usage",
            "category": "analysis",
        },
        {
            "id": "dna_visualization",
            "name": "DNA Visualization Tool",
            "description": "Generate visual representations of DNA sequences",
            "url": "/api/tools/dna_visualization",
            "frontend_url": "/dna_visualization",
            "category": "visualization",
        },
        {
            "id": "sequence_search",
            "name": "Sequence Search",
            "description": "Search for specific DNA and Protein sequences in a database",
            "url": "/api/tools/sequence_search",
            "frontend_url": "/sequence_search",
            "category": "search",
        },
        {
            "id": "blast",
            "name": "BLAST",
            "description": "Find regions of similarity between biological sequences",
            "url": "/api/tools/blast",
            "frontend_url": "/blast",
            "category": "search",
        },
        {
            "id": "phylogenetic_tree",
            "name": "Phylogenetic Tree",
            "description": "Generate evolutionary trees from sequence data",
            "url": "/api/tools/phylogenetic_tree",
            "frontend_url": "/phylogenetic_tree",
            "category": "analysis",
        },
        {
            "id": "primer_design",
            "name": "Primer Design",
            "description": "Design PCR Primers for amplification",
            "url": "/api/tools/primer_design",
            "frontend_url": "/primer_design",
            "category": "design",
        },
        {
            "id": "variant_calling",
            "name": "Variant Calling",
            "description": "Identify variants in sequencing data compared to a reference",
            "url": "/api/tools/variant_calling",
            "frontend_url": "/variant_calling",
            "category": "analysis",
        },
        {
            "id": "motif_finder",
            "name": "Motif Finder",
            "description": "Discover recurring patterns in biological sequences",
            "url": "/api/tools/motif_finder",
            "frontend_url": "/motif_finder",
            "category": "analysis",
        },
        {
            "id": "consensus_maker",
            "name": "Consensus Maker",
            "description": "Generate consensus sequences from multiple alignments",
            "url": "/api/tools/consensus_maker",
            "frontend_url": "/consensus_maker",
            "category": "analysis",
        },
        {
            "id": "data_compression",
            "name": "Data Compression",
            "description": "Compress genomic data for efficient storage and transfer",
            "url": "/api/tools/data_compression",
            "frontend_url": "/data_compression",
            "category": "utility",
        },
        {
            "id": "metagenomics",
            "name": "Metagenomics",
            "description": "Analyze genetic material from environmental samples",
            "url": "/api/tools/metagenomics",
            "frontend_url": "/metagenomics",
            "category": "analysis",
        },
        {
            "id": "protein_structure",
            "name": "Protein Structure Predictor",
            "description": "Predict the structure of proteins from amino acid sequences",
            "url": "/api/tools/protein_structure",
            "frontend_url": "/protein_structure",
            "category": "prediction",
        },
        {
            "id": "sequence_mutator",
            "name": "Sequence Mutator",
            "description": "Introduce mutations to sequences to analyze effects",
            "url": "/api/tools/sequence_mutator",
            "frontend_url": "/sequence_mutator",
            "category": "simulation",
        },
    ]
    return {"tools": tools, "total": len(tools)}


@router.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_active_user)):
    """Verify that the current token is valid"""
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
    }


@router.post("/cleanup-tokens")
async def cleanup_tokens(current_user: User = Depends(get_current_active_user)):
    """Admin endpoint to cleanup expired tokens"""
    # You might want to add admin role checking here
    try:
        deleted_count = await cleanup_expired_tokens()
        return {"message": f"Successfully cleaned up {deleted_count} expired tokens"}
    except Exception as e:
        print(f"Token cleanup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token cleanup failed",
        )


# New Features
# @router.post("/google", response_model=Token)
# async def google_login(request: Request, db: Session = Depends(get_db)):
#     data = await request.json()
#     token = data.get("token")
#     if not token:
#         raise HTTPException(status_code=400, detail="Token is required")
#     # 1. Verify token with Google
#     google_response = requests.get(
#         f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
#     )
#     if google_response.status_code != 200:
#         raise HTTPException(status_code=400, detail="Invalid Google token")
#     google_data = google_response.json()
#     email = google_data["email"]
#     username = google_data.get("name", email.split("@")[0])

#     # 2. Find or create user
#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         user = User(username=username, email=email, hashed_password="", is_active=True)
#         db.add(user)
#         db.commit()
#         db.refresh(user)

#     # 3. Issue your app's JWT
#     access_token = create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}
