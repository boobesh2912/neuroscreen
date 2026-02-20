"""Appointment routes."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.services.booking_service import booking_service


router = APIRouter()


@router.post("", status_code=201)
async def create_appointment(payload: AppointmentCreate, current_user: dict = Depends(get_current_user)):
    try:
        appointment_id = booking_service.create_appointment(current_user["user_id"], payload)
        return {"success": True, "message": "Appointment booked successfully", "appointment_id": appointment_id}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("")
async def my_appointments(status: str | None = None, current_user: dict = Depends(get_current_user)):
    appointments = booking_service.list_user_appointments(current_user["user_id"], status=status)
    return {"success": True, "appointments": appointments, "count": len(appointments)}


@router.patch("/{appointment_id}")
async def update_appointment(
    appointment_id: str,
    payload: AppointmentUpdate,
    current_user: dict = Depends(get_current_user),
):
    try:
        booking_service.update_appointment(appointment_id, payload)
        return {"success": True, "message": "Appointment status updated"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
