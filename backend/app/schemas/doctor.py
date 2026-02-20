"""Doctor schemas."""

from pydantic import BaseModel, Field


class DoctorBase(BaseModel):
    full_name: str
    email: str
    phone_number: str
    specialization: str
    qualification: str
    experience_years: int = Field(ge=0)
    city: str
    state: str
    consultation_fee: float = Field(ge=0)
    sub_specialties: str | None = None
    hospital_affiliation: str | None = None
    clinic_address: str | None = None
    about: str | None = None
    languages: str | None = None


class DoctorCreate(DoctorBase):
    pass


class DoctorResponse(DoctorBase):
    id: str
    rating: float = 0.0
    total_reviews: int = 0
    is_available: bool = True


class DoctorAvailability(BaseModel):
    id: str
    doctor_id: str
    day_of_week: int
    start_time: str
    end_time: str
    slot_duration: int = 30
    is_active: bool = True


class DoctorReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_text: str | None = None
    appointment_id: str | None = None


class DoctorReview(BaseModel):
    id: str
    doctor_id: str
    user_id: str
    rating: int
    review_text: str | None = None
    created_at: str
    first_name: str | None = None
    last_name: str | None = None


class DoctorDetail(BaseModel):
    doctor: DoctorResponse
    availability: list[DoctorAvailability] = []
    reviews: list[DoctorReview] = []
