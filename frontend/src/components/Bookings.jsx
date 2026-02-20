import { useState, useEffect } from 'react';
import AppShell from './AppShell';
import { Calendar, Clock, MapPin, Star, Phone, Award, DollarSign, ChevronRight, AlertCircle } from 'lucide-react';
import { bookingAPI, getApiErrorMessage } from '../api';

const cardClass = 'rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-6 shadow-soft';

const Bookings = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('find-doctors');
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ city: '', specialization: '' });
  const [bookingForm, setBookingForm] = useState({
    appointment_date: '',
    appointment_time: '',
    symptoms: '',
    notes: ''
  });
  const [showBookingModal, setShowBookingModal] = useState(false);

  useEffect(() => {
    setError('');
    setSuccess('');
    if (activeTab === 'find-doctors') {
      fetchDoctors();
    } else if (activeTab === 'my-appointments') {
      fetchAppointments();
    }
  }, [activeTab]);

  const fetchDoctors = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await bookingAPI.getDoctors(filters.city, filters.specialization);
      setDoctors(response.data.doctors);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to load doctors. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  const fetchAppointments = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await bookingAPI.getAppointments();
      setAppointments(response.data.appointments);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to load appointments. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  const handleBookAppointment = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await bookingAPI.bookAppointment({
        doctor_id: selectedDoctor.id,
        ...bookingForm
      });

      setSuccess('Appointment booked successfully.');
      setShowBookingModal(false);
      setBookingForm({
        appointment_date: '',
        appointment_time: '',
        symptoms: '',
        notes: ''
      });
      setActiveTab('my-appointments');
      fetchAppointments();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to book appointment. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  const handleCancelAppointment = async (appointmentId) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) return;

    try {
      await bookingAPI.updateAppointment(appointmentId, {
        status: 'cancelled',
        cancellation_reason: 'User cancelled'
      });

      setSuccess('Appointment cancelled successfully.');
      fetchAppointments();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to cancel appointment.'));
    }
  };

  const openBookingModal = (doctor) => {
    setSelectedDoctor(doctor);
    setShowBookingModal(true);
  };

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
      />
    ));
  };

  const getStatusBadge = (status) => {
    const styles = {
      scheduled: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
      'no-show': 'bg-gray-100 text-gray-800',
      no_show: 'bg-gray-100 text-gray-800'
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[status] || styles.scheduled}`}>
        {status.charAt(0).toUpperCase() + status.slice(1).replace('-', ' ').replace('_', ' ')}
      </span>
    );
  };

  return (
    <AppShell
      user={user}
      onLogout={onLogout}
      title="Doctor Consultations"
      subtitle="Book appointments with specialized neurologists for Parkinson's disease screening and treatment."
    >
      {error ? (
        <div className="mb-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm font-semibold text-rose-700">
          {error}
        </div>
      ) : null}
      {success ? (
        <div className="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm font-semibold text-emerald-700">
          {success}
        </div>
      ) : null}

      {/* Tabs */}
      <div className="mb-6 flex gap-2 border-b border-[var(--line)]">
        <button
          onClick={() => setActiveTab('find-doctors')}
          className={`px-6 py-3 font-semibold transition-colors ${
            activeTab === 'find-doctors'
              ? 'border-b-2 border-[var(--brand-700)] text-[var(--brand-700)]'
              : 'text-[var(--ink-600)] hover:text-[var(--ink-900)]'
          }`}
        >
          Find Doctors
        </button>
        <button
          onClick={() => setActiveTab('my-appointments')}
          className={`px-6 py-3 font-semibold transition-colors ${
            activeTab === 'my-appointments'
              ? 'border-b-2 border-[var(--brand-700)] text-[var(--brand-700)]'
              : 'text-[var(--ink-600)] hover:text-[var(--ink-900)]'
          }`}
        >
          My Appointments
        </button>
      </div>

      {/* Find Doctors Tab */}
      {activeTab === 'find-doctors' && (
        <div className="space-y-6">
          {/* Filters */}
          <div className={cardClass}>
            <h3 className="mb-4 font-display text-lg font-bold">Filter Doctors</h3>
            <div className="grid gap-4 md:grid-cols-3">
              <input
                type="text"
                placeholder="City"
                value={filters.city}
                onChange={(e) => setFilters({ ...filters, city: e.target.value })}
                className="rounded-lg border border-[var(--line)] px-4 py-2"
              />
              <select
                value={filters.specialization}
                onChange={(e) => setFilters({ ...filters, specialization: e.target.value })}
                className="rounded-lg border border-[var(--line)] px-4 py-2"
              >
                <option value="">All Specializations</option>
                <option value="Movement Disorders Specialist">Movement Disorders</option>
                <option value="General Neurologist">General Neurology</option>
                <option value="Parkinson's Disease Specialist">Parkinson's Specialist</option>
              </select>
              <button
                onClick={fetchDoctors}
                disabled={loading}
                className="rounded-lg bg-[var(--brand-700)] px-6 py-2 font-semibold text-white hover:bg-[var(--brand-800)]"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>

          {/* Doctors List */}
          {loading ? (
            <div className="text-center py-12">Loading doctors...</div>
          ) : doctors.length === 0 ? (
            <div className={cardClass}>
              <p className="text-center text-[var(--ink-600)]">No doctors found. Try adjusting your filters.</p>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2">
              {doctors.map((doctor) => (
                <article key={doctor.id} className={cardClass}>
                  <div className="mb-4 flex items-start justify-between">
                    <div>
                      <h3 className="font-display text-xl font-bold text-[var(--ink-900)]">
                        Dr. {doctor.full_name}
                      </h3>
                      <p className="text-sm text-[var(--brand-700)]">{doctor.specialization}</p>
                      {doctor.sub_specialties && (
                        <p className="text-xs text-[var(--ink-600)]">{doctor.sub_specialties}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      {renderStars(Math.round(doctor.rating || 0))}
                      <span className="ml-1 text-sm text-[var(--ink-600)]">
                        ({doctor.total_reviews || 0})
                      </span>
                    </div>
                  </div>

                  <div className="mb-4 space-y-2 text-sm text-[var(--ink-700)]">
                    <div className="flex items-center gap-2">
                      <Award className="h-4 w-4 text-[var(--brand-700)]" />
                      <span>{doctor.qualification} - {doctor.experience_years} years exp</span>
                    </div>
                    {doctor.hospital_affiliation && (
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-[var(--brand-700)]" />
                        <span>{doctor.hospital_affiliation}, {doctor.city}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-[var(--brand-700)]" />
                      <span>{doctor.phone_number}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-4 w-4 text-[var(--brand-700)]" />
                      <span className="font-semibold">INR {doctor.consultation_fee} consultation fee</span>
                    </div>
                  </div>

                  {doctor.about && (
                    <p className="mb-4 text-sm text-[var(--ink-600)] line-clamp-2">{doctor.about}</p>
                  )}

                  <button
                    onClick={() => openBookingModal(doctor)}
                    className="w-full rounded-lg bg-[var(--brand-700)] px-4 py-2 font-semibold text-white hover:bg-[var(--brand-800)] flex items-center justify-center gap-2"
                  >
                    Book Appointment
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </article>
              ))}
            </div>
          )}
        </div>
      )}

      {/* My Appointments Tab */}
      {activeTab === 'my-appointments' && (
        <div className="space-y-6">
          {loading ? (
            <div className="text-center py-12">Loading appointments...</div>
          ) : appointments.length === 0 ? (
            <div className={cardClass}>
              <div className="text-center py-8">
                <AlertCircle className="h-12 w-12 mx-auto mb-4 text-[var(--ink-400)]" />
                <p className="text-[var(--ink-600)]">You have no appointments yet.</p>
                <button
                  onClick={() => setActiveTab('find-doctors')}
                  className="mt-4 text-[var(--brand-700)] font-semibold hover:underline"
                >
                  Book your first appointment
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {appointments.map((appointment) => (
                <article key={appointment.id} className={cardClass}>
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-display text-lg font-bold text-[var(--ink-900)]">
                        Dr. {appointment.doctor_name}
                      </h3>
                      <p className="text-sm text-[var(--ink-600)]">{appointment.specialization}</p>
                      {appointment.hospital_affiliation && (
                        <p className="text-sm text-[var(--ink-600)]">{appointment.hospital_affiliation}</p>
                      )}
                    </div>
                    {getStatusBadge(appointment.status)}
                  </div>

                  <div className="grid gap-3 md:grid-cols-2 mb-4">
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="h-4 w-4 text-[var(--brand-700)]" />
                      <span>{new Date(appointment.appointment_date).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-4 w-4 text-[var(--brand-700)]" />
                      <span>{appointment.appointment_time}</span>
                    </div>
                    {appointment.risk_score && (
                      <div className="flex items-center gap-2 text-sm">
                        <AlertCircle className="h-4 w-4 text-orange-500" />
                        <span>Risk Score: {appointment.risk_score}%</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-sm">
                      <DollarSign className="h-4 w-4 text-[var(--brand-700)]" />
                      <span>INR {appointment.consultation_fee}</span>
                    </div>
                  </div>

                  {appointment.symptoms && (
                    <div className="mb-4">
                      <p className="text-xs font-semibold text-[var(--ink-600)] mb-1">Symptoms:</p>
                      <p className="text-sm text-[var(--ink-700)]">{appointment.symptoms}</p>
                    </div>
                  )}

                  {appointment.status === 'scheduled' && (
                    <button
                      onClick={() => handleCancelAppointment(appointment.id)}
                      className="text-sm text-red-600 hover:underline"
                    >
                      Cancel Appointment
                    </button>
                  )}
                </article>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Booking Modal */}
      {showBookingModal && selectedDoctor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full">
            <h2 className="font-display text-2xl font-bold mb-4">
              Book Appointment with Dr. {selectedDoctor.full_name}
            </h2>

            <form onSubmit={handleBookAppointment} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Appointment Date</label>
                <input
                  type="date"
                  required
                  min={new Date().toISOString().split('T')[0]}
                  value={bookingForm.appointment_date}
                  onChange={(e) => setBookingForm({ ...bookingForm, appointment_date: e.target.value })}
                  className="w-full rounded-lg border border-[var(--line)] px-4 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Appointment Time</label>
                <input
                  type="time"
                  required
                  value={bookingForm.appointment_time}
                  onChange={(e) => setBookingForm({ ...bookingForm, appointment_time: e.target.value })}
                  className="w-full rounded-lg border border-[var(--line)] px-4 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Symptoms (Optional)</label>
                <textarea
                  rows={3}
                  value={bookingForm.symptoms}
                  onChange={(e) => setBookingForm({ ...bookingForm, symptoms: e.target.value })}
                  placeholder="Describe your symptoms..."
                  className="w-full rounded-lg border border-[var(--line)] px-4 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Additional Notes (Optional)</label>
                <textarea
                  rows={2}
                  value={bookingForm.notes}
                  onChange={(e) => setBookingForm({ ...bookingForm, notes: e.target.value })}
                  placeholder="Any additional information..."
                  className="w-full rounded-lg border border-[var(--line)] px-4 py-2"
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowBookingModal(false)}
                  className="flex-1 rounded-lg border border-[var(--line)] px-4 py-2 font-semibold hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 rounded-lg bg-[var(--brand-700)] px-4 py-2 font-semibold text-white hover:bg-[var(--brand-800)] disabled:opacity-50"
                >
                  {loading ? 'Booking...' : 'Confirm Booking'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
};

export default Bookings;
