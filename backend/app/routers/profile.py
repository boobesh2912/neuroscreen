"""User profile routes."""

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.profile import EmergencyContactCreate
from app.services.booking_service import booking_service


router = APIRouter()


@router.get("/profile")
async def profile(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": current_user}


@router.post("/profile/emergency", status_code=201)
async def add_emergency_contact(payload: EmergencyContactCreate, current_user: dict = Depends(get_current_user)):
    contact_id = booking_service.add_emergency_contact(
        user_id=current_user["user_id"],
        name=str(payload.name),
        relationship=str(payload.relationship),
        phone=str(payload.phone),
        email=str(payload.email) if payload.email else None,
        is_primary=payload.is_primary,
    )
    return {"success": True, "message": "Emergency contact added", "contact_id": contact_id}


@router.get("/profile/emergency")
async def list_emergency_contacts(current_user: dict = Depends(get_current_user)):
    contacts = booking_service.get_emergency_contacts(current_user["user_id"])
    return {"success": True, "contacts": contacts}
