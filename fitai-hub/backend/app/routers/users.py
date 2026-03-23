from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User, UserProfile
from app.schemas.user import UserProfileUpdate, UserProfileResponse, UserPublicResponse, UpdateUserRequest
from app.schemas.auth import UserBasicResponse
import uuid

router = APIRouter(prefix="/users", tags=["Users"])


# --- PERFIL PROPIO ---
@router.get("/me", response_model=UserBasicResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserBasicResponse.model_validate(current_user)


@router.put("/me", response_model=UserBasicResponse)
async def update_me(
    data: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.name is not None:
        current_user.name = data.name
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return UserBasicResponse.model_validate(current_user)


# --- PERFIL FITNESS ---
@router.get("/me/profile", response_model=UserProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return UserProfileResponse.model_validate(profile)


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_my_profile(
    data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        # Crear perfil si no existe
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
        )
        db.add(profile)

    # Actualizar solo los campos enviados
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return UserProfileResponse.model_validate(profile)


# --- PERFILES PÚBLICOS ---
@router.get("/search", response_model=list[UserPublicResponse])
async def search_users(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if len(q) < 2:
        raise HTTPException(
            status_code=400,
            detail="La búsqueda debe tener al menos 2 caracteres"
        )
    result = await db.execute(
        select(User).where(
            (User.username.ilike(f"%{q}%") | User.name.ilike(f"%{q}%"))
            & (User.is_active == True)
        ).limit(20)
    )
    users = result.scalars().all()
    return [UserPublicResponse.model_validate(u) for u in users]


@router.get("/{username}", response_model=UserPublicResponse)
async def get_public_profile(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(User).where(
            (User.username == username) & (User.is_active == True)
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserPublicResponse.model_validate(user)