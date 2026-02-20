"""Doctor booking and appointment service."""

from datetime import datetime
import json
import uuid

from app.core.database import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.schemas.doctor import DoctorCreate, DoctorReviewCreate


class BookingService:
    def list_doctors(self, city: str | None = None, specialization: str | None = None, available: bool = True) -> list[dict]:
        query = "SELECT * FROM doctors WHERE 1=1"
        params: list = []

        if available:
            query += " AND is_available = 1"
        if city:
            query += " AND city = ?"
            params.append(city)
        if specialization:
            query += " AND specialization = ?"
            params.append(specialization)

        query += " ORDER BY rating DESC, experience_years DESC"

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def get_doctor(self, doctor_id: str) -> dict | None:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_doctor_availability(self, doctor_id: str) -> list[dict]:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT * FROM doctor_availability
                WHERE doctor_id = ? AND is_active = 1
                ORDER BY day_of_week, start_time
                """,
                (doctor_id,),
            )
            return [dict(row) for row in cur.fetchall()]

    def add_doctor(self, payload: DoctorCreate) -> str:
        doctor_id = str(uuid.uuid4())
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM doctors WHERE email = ?", (payload.email,))
            if cur.fetchone():
                raise ValueError("Doctor with this email already exists")

            cur.execute(
                """
                INSERT INTO doctors (
                    id, full_name, email, phone_number, specialization,
                    sub_specialties, qualification, experience_years,
                    hospital_affiliation, clinic_address, city, state,
                    consultation_fee, about, languages, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doctor_id,
                    payload.full_name,
                    str(payload.email),
                    payload.phone_number,
                    payload.specialization,
                    payload.sub_specialties,
                    payload.qualification,
                    payload.experience_years,
                    payload.hospital_affiliation,
                    payload.clinic_address,
                    payload.city,
                    payload.state,
                    payload.consultation_fee,
                    payload.about,
                    payload.languages,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        return doctor_id

    def create_appointment(self, user_id: str, payload: AppointmentCreate) -> str:
        appointment_id = str(uuid.uuid4())
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM doctors WHERE id = ?", (payload.doctor_id,))
            if cur.fetchone() is None:
                raise ValueError("Doctor not found")

            cur.execute(
                """
                INSERT INTO appointments (
                    id, user_id, doctor_id, test_result_id, appointment_date,
                    appointment_time, status, symptoms, notes, risk_score, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    appointment_id,
                    user_id,
                    payload.doctor_id,
                    payload.test_result_id,
                    payload.appointment_date,
                    payload.appointment_time,
                    "scheduled",
                    payload.symptoms,
                    payload.notes,
                    payload.risk_score,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        return appointment_id

    def list_user_appointments(self, user_id: str, status: str | None = None) -> list[dict]:
        query = (
            """
            SELECT a.*, d.full_name AS doctor_name, d.specialization,
                   d.hospital_affiliation, d.consultation_fee
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.user_id = ?
            """
        )
        params: list = [user_id]
        if status:
            query += " AND a.status = ?"
            params.append(status)
        query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def update_appointment(self, appointment_id: str, payload: AppointmentUpdate) -> None:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE appointments
                SET status = ?, updated_at = ?, cancellation_reason = ?
                WHERE id = ?
                """,
                (
                    payload.status,
                    datetime.now().isoformat(),
                    payload.cancellation_reason,
                    appointment_id,
                ),
            )
            if cur.rowcount == 0:
                raise ValueError("Appointment not found")
            conn.commit()

    def add_review(self, doctor_id: str, user_id: str, payload: DoctorReviewCreate) -> str:
        review_id = str(uuid.uuid4())
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO doctor_reviews (id, doctor_id, user_id, appointment_id, rating, review_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review_id,
                    doctor_id,
                    user_id,
                    payload.appointment_id,
                    payload.rating,
                    payload.review_text,
                    datetime.now().isoformat(),
                ),
            )

            cur.execute(
                "SELECT AVG(rating) AS avg_rating, COUNT(*) AS total_reviews FROM doctor_reviews WHERE doctor_id = ?",
                (doctor_id,),
            )
            stats = cur.fetchone()
            cur.execute(
                "UPDATE doctors SET rating = ?, total_reviews = ?, updated_at = ? WHERE id = ?",
                (stats["avg_rating"], stats["total_reviews"], datetime.now().isoformat(), doctor_id),
            )
            conn.commit()
        return review_id

    def list_reviews(self, doctor_id: str) -> list[dict]:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT r.*, u.first_name, u.last_name
                FROM doctor_reviews r
                JOIN users u ON r.user_id = u.id
                WHERE r.doctor_id = ?
                ORDER BY r.created_at DESC
                """,
                (doctor_id,),
            )
            return [dict(row) for row in cur.fetchall()]

    def add_emergency_contact(
        self,
        user_id: str,
        name: str,
        relationship: str,
        phone: str,
        email: str | None = None,
        is_primary: bool = False,
    ) -> str:
        contact_id = str(uuid.uuid4())
        with get_db() as conn:
            cur = conn.cursor()
            if is_primary:
                cur.execute("UPDATE emergency_contacts SET is_primary = 0 WHERE user_id = ?", (user_id,))

            cur.execute(
                """
                INSERT INTO emergency_contacts (id, user_id, name, relationship, phone_number, email, is_primary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (contact_id, user_id, name, relationship, phone, email, int(is_primary)),
            )
            conn.commit()
        return contact_id

    def get_emergency_contacts(self, user_id: str) -> list[dict]:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM emergency_contacts WHERE user_id = ? ORDER BY is_primary DESC",
                (user_id,),
            )
            return [dict(row) for row in cur.fetchall()]

    def save_test_result(
        self,
        user_id: str,
        test_type: str,
        prediction: str,
        confidence: float,
        features: dict,
        audio_path: str | None,
    ) -> str:
        result_id = str(uuid.uuid4())
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO test_results (id, user_id, test_type, test_date, prediction, confidence, features, audio_file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result_id,
                    user_id,
                    test_type,
                    datetime.now().isoformat(),
                    prediction,
                    confidence,
                    json.dumps(features, ensure_ascii=False),
                    audio_path,
                ),
            )
            conn.commit()
        return result_id

    def get_user_tests(self, user_id: str) -> list[dict]:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM test_results WHERE user_id = ? ORDER BY test_date DESC", (user_id,))
            return [dict(row) for row in cur.fetchall()]


booking_service = BookingService()
