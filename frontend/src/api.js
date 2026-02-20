import axios from 'axios';

const API_ROOT_URL = (import.meta.env.VITE_API_ROOT_URL || '').trim().replace(/\/$/, '');
const API_BASE_URL = API_ROOT_URL ? `${API_ROOT_URL}/api` : '/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  verify: () => api.get('/auth/verify'),
};

// Analysis APIs
export const analysisAPI = {
  analyzeAudio: (audioFile) => {
    const formData = new FormData();
    formData.append('audio', audioFile);
    return api.post('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  analyzeAudioMultiDisease: (audioFile, testType = 'sustained_vowel') => {
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('test_type', testType);
    return api.post('/analyze/multi-disease', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// Dashboard APIs
export const dashboardAPI = {
  getDashboard: () => api.get('/dashboard'),
  getTestResult: (testId) => api.get(`/results/${testId}`),
};

// Profile APIs
export const profileAPI = {
  getProfile: () => api.get('/profile'),
  addEmergencyContact: (contact) => api.post('/profile/emergency', contact),
  getEmergencyContacts: () => api.get('/profile/emergency'),
};

// Booking APIs
export const bookingAPI = {
  getDoctors: (city, specialization) => {
    const params = new URLSearchParams();
    if (city) params.append('city', city);
    if (specialization) params.append('specialization', specialization);
    return api.get(`/doctors?${params.toString()}`);
  },
  getDoctorById: (doctorId) => api.get(`/doctors/${doctorId}`),
  bookAppointment: (appointmentData) => api.post('/appointments', appointmentData),
  getAppointments: (status) => {
    const params = status ? `?status=${status}` : '';
    return api.get(`/appointments${params}`);
  },
  updateAppointment: (appointmentId, data) => api.patch(`/appointments/${appointmentId}`, data),
  addReview: (doctorId, reviewData) => api.post(`/doctors/${doctorId}/reviews`, reviewData),
  getReviews: (doctorId) => api.get(`/doctors/${doctorId}/reviews`),
};

// Helper function to get image URLs
export const getImageUrl = (path) => {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  return API_ROOT_URL ? `${API_ROOT_URL}${path}` : path;
};

export const getApiErrorMessage = (error, fallbackMessage = 'Request failed. Please try again.') => {
  if (error?.response?.data?.error) {
    return error.response.data.error;
  }

  if (error?.code === 'ERR_NETWORK' || error?.code === 'ECONNREFUSED') {
    return 'Cannot reach backend API. Check your VITE_API_ROOT_URL configuration and backend status.';
  }

  if (error?.response?.status === 503) {
    return 'Service is temporarily unavailable. Please try again shortly.';
  }

  return fallbackMessage;
};

export default api;
