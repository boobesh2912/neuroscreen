"""Doctor routes."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.schemas.doctor import DoctorCreate, DoctorReviewCreate
from app.services.booking_service import booking_service


router = APIRouter()


@router.get("")
async def list_doctors(specialization: str | None = None, city: str | None = None, available: bool = True):
    doctors = booking_service.list_doctors(city=city, specialization=specialization, available=available)
    return {"success": True, "doctors": doctors, "count": len(doctors)}


@router.get("/{doctor_id}")
async def get_doctor(doctor_id: str):
    doctor = booking_service.get_doctor(doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctor["availability"] = booking_service.get_doctor_availability(doctor_id)
    doctor["reviews"] = booking_service.list_reviews(doctor_id)

    return {
        "success": True,
        "doctor": doctor,
    }


@router.post("", status_code=201)
async def add_doctor(payload: DoctorCreate, current_user: dict = Depends(get_current_user)):
    try:
        doctor_id = booking_service.add_doctor(payload)
        return {"success": True, "message": "Doctor added successfully", "doctor_id": doctor_id}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{doctor_id}/reviews", status_code=201)
async def add_review(
    doctor_id: str,
    payload: DoctorReviewCreate,
    current_user: dict = Depends(get_current_user),
):
    review_id = booking_service.add_review(doctor_id, current_user["user_id"], payload)
    return {"success": True, "message": "Review added successfully", "review_id": review_id}


@router.get("/{doctor_id}/reviews")
async def get_reviews(doctor_id: str):
    reviews = booking_service.list_reviews(doctor_id)
    return {"success": True, "reviews": reviews, "count": len(reviews)}
