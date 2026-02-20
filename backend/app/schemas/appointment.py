"""Appointment schemas."""

from typing import Literal

from pydantic import BaseModel, Field


class AppointmentCreate(BaseModel):
    doctor_id: str
    appointment_date: str
    appointment_time: str
    test_result_id: str | None = None
    symptoms: str | None = None
    notes: str | None = None
    risk_score: int | None = Field(default=None, ge=0, le=100)


class AppointmentUpdate(BaseModel):
    status: Literal["scheduled", "completed", "cancelled", "no_show"]
    cancellation_reason: str | None = None


class AppointmentResponse(BaseModel):
    id: str
    user_id: str
    doctor_id: str
    appointment_date: str
    appointment_time: str
    status: str
    booking_type: str
    symptoms: str | None = None
    notes: str | None = None
    risk_score: int | None = None
    created_at: str
    updated_at: str | None = None
    cancellation_reason: str | None = None
    doctor_name: str | None = None
    specialization: str | None = None
    hospital_affiliation: str | None = None
    consultation_fee: float | None = None
