"""
User Profile API Endpoints.

CRUD operations for user profile management:
- GET /api/profile - Get current user's profile
- POST /api/profile - Create new profile
- PUT /api/profile - Update profile
- DELETE /api/profile - Delete profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.database import get_db, UserProfile
from models.schemas import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    TokenData
)
from api.auth import get_current_user
from services.calculations import (
    calculate_tdee,
    calculate_macros,
    calculate_bmr
)

router = APIRouter()


@router.get("", response_model=UserProfileResponse, tags=["Profile"])
async def get_profile(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile.

    Returns:
        UserProfileResponse with all profile data

    Raises:
        HTTPException 404: If profile doesn't exist
    """
    profile = db.query(UserProfile).filter(UserProfile.id == current_user.user_id).first()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create a profile first."
        )

    return profile


@router.post("", response_model=UserProfileResponse, tags=["Profile"], status_code=status.HTTP_201_CREATED)
async def create_profile(
    request: UserProfileCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new user profile.

    Args:
        request: UserProfileCreate with profile data

    Returns:
        UserProfileResponse with created profile

    Raises:
        HTTPException 400: If profile already exists
    """
    # Check if profile already exists
    existing_profile = db.query(UserProfile).filter(UserProfile.id == current_user.user_id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT to update."
        )

    # Create new profile
    profile = UserProfile(
        id=current_user.user_id,
        email=current_user.email,
        **request.dict(exclude={"email"})
    )

    # Calculate TDEE and macros if sufficient data provided
    if all([profile.age, profile.sex, profile.height_inches, profile.current_weight_lbs]):
        try:
            # Calculate BMR and TDEE
            profile.bmr = calculate_bmr(
                weight_lbs=profile.current_weight_lbs,
                height_inches=profile.height_inches,
                age=profile.age,
                sex=profile.sex
            )

            profile.tdee = calculate_tdee(
                bmr=profile.bmr,
                activity_level="sedentary"  # Default, can be updated later
            )

            # Calculate target calories based on goal
            if profile.goal_type == "cut":
                profile.target_calories = int(profile.tdee - 500)  # -500 cal deficit
            elif profile.goal_type == "bulk":
                profile.target_calories = int(profile.tdee + 300)  # +300 cal surplus
            else:  # recomp or maintain
                profile.target_calories = int(profile.tdee)

            # Calculate macros
            macros = calculate_macros(
                target_calories=profile.target_calories,
                weight_lbs=profile.current_weight_lbs,
                goal_type=profile.goal_type or "maintain"
            )

            profile.target_protein_g = macros["protein_g"]
            profile.target_carbs_g = macros["carbs_g"]
            profile.target_fat_g = macros["fat_g"]

        except Exception as e:
            # If calculation fails, still create profile without calculated fields
            print(f"Warning: Failed to calculate TDEE/macros: {e}")

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


@router.put("", response_model=UserProfileResponse, tags=["Profile"])
async def update_profile(
    request: UserProfileUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile.

    Args:
        request: UserProfileUpdate with fields to update (all optional)

    Returns:
        UserProfileResponse with updated profile

    Raises:
        HTTPException 404: If profile doesn't exist
    """
    profile = db.query(UserProfile).filter(UserProfile.id == current_user.user_id).first()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create a profile first."
        )

    # Update profile fields (only non-None values)
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    # Recalculate TDEE and macros if relevant fields changed
    if any(k in update_data for k in ["age", "sex", "height_inches", "current_weight_lbs", "goal_type"]):
        if all([profile.age, profile.sex, profile.height_inches, profile.current_weight_lbs]):
            try:
                profile.bmr = calculate_bmr(
                    weight_lbs=profile.current_weight_lbs,
                    height_inches=profile.height_inches,
                    age=profile.age,
                    sex=profile.sex
                )

                profile.tdee = calculate_tdee(
                    bmr=profile.bmr,
                    activity_level="sedentary"
                )

                if profile.goal_type == "cut":
                    profile.target_calories = int(profile.tdee - 500)
                elif profile.goal_type == "bulk":
                    profile.target_calories = int(profile.tdee + 300)
                else:
                    profile.target_calories = int(profile.tdee)

                macros = calculate_macros(
                    target_calories=profile.target_calories,
                    weight_lbs=profile.current_weight_lbs,
                    goal_type=profile.goal_type or "maintain"
                )

                profile.target_protein_g = macros["protein_g"]
                profile.target_carbs_g = macros["carbs_g"]
                profile.target_fat_g = macros["fat_g"]

            except Exception as e:
                print(f"Warning: Failed to recalculate TDEE/macros: {e}")

    db.commit()
    db.refresh(profile)

    return profile


@router.delete("", status_code=status.HTTP_204_NO_CONTENT, tags=["Profile"])
async def delete_profile(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user profile.

    Note: This only deletes the profile, not the Supabase Auth account.

    Raises:
        HTTPException 404: If profile doesn't exist
    """
    profile = db.query(UserProfile).filter(UserProfile.id == current_user.user_id).first()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found."
        )

    db.delete(profile)
    db.commit()

    return None
