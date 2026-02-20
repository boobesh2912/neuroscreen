"""Seed sample doctors and weekday availability into the production database."""

from datetime import datetime
from pathlib import Path
import uuid
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.database import get_db, init_database
from app.services.booking_service import booking_service
from app.schemas.doctor import DoctorCreate


DOCTORS = [
    DoctorCreate(
        full_name="Rajesh Kumar",
        email="dr.rajesh.kumar@mediguardian.com",
        phone_number="+91-9876543210",
        specialization="Movement Disorders Specialist",
        sub_specialties="Parkinson's Disease, Essential Tremor, Dystonia",
        qualification="MBBS, MD (Neurology), DM (Movement Disorders)",
        experience_years=15,
        hospital_affiliation="Apollo Hospitals",
        clinic_address="123 MG Road, Apollo Hospitals",
        city="Bangalore",
        state="Karnataka",
        consultation_fee=1500.0,
        about=(
            "Movement disorders specialist focused on Parkinson's diagnostics and treatment, "
            "including deep brain stimulation care pathways."
        ),
        languages="English, Hindi, Kannada",
    ),
    DoctorCreate(
        full_name="Priya Sharma",
        email="dr.priya.sharma@mediguardian.com",
        phone_number="+91-9876543211",
        specialization="General Neurologist",
        sub_specialties="Neurodegenerative Disorders, Stroke, Epilepsy",
        qualification="MBBS, MD (Neurology)",
        experience_years=12,
        hospital_affiliation="Fortis Hospital",
        clinic_address="456 Park Street, Fortis Hospital",
        city="Mumbai",
        state="Maharashtra",
        consultation_fee=1200.0,
        about=(
            "General neurologist with focus on early detection of neurodegenerative disease and "
            "longitudinal management."
        ),
        languages="English, Hindi, Marathi",
    ),
    DoctorCreate(
        full_name="Anil Mehta",
        email="dr.anil.mehta@mediguardian.com",
        phone_number="+91-9876543212",
        specialization="Parkinson's Disease Specialist",
        sub_specialties="Deep Brain Stimulation, Gait Disorders",
        qualification="MBBS, MD (Neurology), DM (Neurology)",
        experience_years=18,
        hospital_affiliation="AIIMS",
        clinic_address="All India Institute of Medical Sciences, Ansari Nagar",
        city="Delhi",
        state="Delhi",
        consultation_fee=2000.0,
        about=(
            "Parkinson's disease specialist with extensive advanced-therapy experience and "
            "multidisciplinary rehabilitation planning."
        ),
        languages="English, Hindi, Punjabi",
    ),
]


def _seed_availability(doctor_id: str) -> None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM doctor_availability WHERE doctor_id = ?", (doctor_id,))
        if cur.fetchone():
            return

        for day in range(1, 6):
            cur.execute(
                """
                INSERT INTO doctor_availability (
                    id, doctor_id, day_of_week, start_time, end_time, slot_duration, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (str(uuid.uuid4()), doctor_id, day, "09:00", "17:00", 30, 1),
            )
        conn.commit()


def seed_doctors() -> None:
    init_database()
    created = 0

    for doctor in DOCTORS:
        try:
            doctor_id = booking_service.add_doctor(doctor)
            _seed_availability(doctor_id)
            created += 1
            print(f"created doctor={doctor.full_name} id={doctor_id}")
        except ValueError:
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id FROM doctors WHERE email = ?", (str(doctor.email),))
                row = cur.fetchone()
                if row:
                    _seed_availability(row["id"])
            print(f"exists doctor={doctor.full_name}")

    print(f"seed complete: {created} created, {len(DOCTORS) - created} existing")
    print(f"finished at {datetime.now().isoformat()}")


if __name__ == "__main__":
    seed_doctors()
