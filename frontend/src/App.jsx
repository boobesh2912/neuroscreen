import { lazy, Suspense, useEffect, useState } from 'react';
import { BrowserRouter as Router, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { authAPI } from './api';

const Landing = lazy(() => import('./components/Landing'));
const About = lazy(() => import('./components/About'));
const HowItWorks = lazy(() => import('./components/HowItWorks'));
const Pricing = lazy(() => import('./components/Pricing'));
const FAQ = lazy(() => import('./components/FAQ'));
const Contact = lazy(() => import('./components/Contact'));
const Login = lazy(() => import('./components/Login'));
const Register = lazy(() => import('./components/Register'));
const Dashboard = lazy(() => import('./components/Dashboard'));
const TestPage = lazy(() => import('./components/TestPage'));
const Learning = lazy(() => import('./components/Learning'));
const Profile = lazy(() => import('./components/Profile'));
const Bookings = lazy(() => import('./components/Bookings'));
const NotFound = lazy(() => import('./components/NotFound'));

const DEFAULT_TITLE = 'NeuroScreen | Voice-Based Neurological Screening';
const DEFAULT_DESCRIPTION =
  'NeuroScreen helps users run structured voice screenings, monitor neurological risk trends, and share insights with clinicians.';

const PAGE_METADATA = {
  '/': {
    title: 'NeuroScreen | Early Neurological Screening',
    description: 'Voice-based early signal detection platform for neurological risk support and trend tracking.',
  },
  '/about': {
    title: 'About NeuroScreen',
    description: 'Learn how NeuroScreen supports neurological risk screening with interpretable voice biomarkers.',
  },
  '/how-it-works': {
    title: 'How NeuroScreen Works',
    description: 'Understand the NeuroScreen workflow from voice capture to risk scoring and longitudinal monitoring.',
  },
  '/pricing': {
    title: 'NeuroScreen Pricing',
    description: 'Choose a NeuroScreen plan for voice screenings, analytics, and ongoing risk trend tracking.',
  },
  '/faq': {
    title: 'NeuroScreen FAQ',
    description: 'Frequently asked questions about NeuroScreen, data handling, and clinical screening support.',
  },
  '/contact': {
    title: 'Contact NeuroScreen',
    description: 'Get in touch with NeuroScreen support and partnerships for product or clinical workflow questions.',
  },
  '/login': {
    title: 'Sign In | NeuroScreen',
    description: 'Sign in to NeuroScreen to access voice tests, dashboards, and consultation workflows.',
  },
  '/register': {
    title: 'Create Account | NeuroScreen',
    description: 'Create your NeuroScreen account to start voice-based neurological risk tracking.',
  },
  '/dashboard': {
    title: 'Dashboard | NeuroScreen',
    description: 'Monitor risk trends, confidence levels, and historical NeuroScreen assessments.',
  },
  '/test': {
    title: 'Voice Assessment | NeuroScreen',
    description: 'Capture or upload voice recordings and run NeuroScreen biomarker analysis.',
  },
  '/learning': {
    title: 'Learning Hub | NeuroScreen',
    description: 'Explore educational content and routines that support neurological health awareness.',
  },
  '/profile': {
    title: 'Profile | NeuroScreen',
    description: 'Manage account settings and emergency contact details in NeuroScreen.',
  },
  '/bookings': {
    title: 'Consultations | NeuroScreen',
    description: 'Find specialists and book consultation appointments from NeuroScreen.',
  },
};

const upsertMeta = (selector, attributes) => {
  let node = document.head.querySelector(selector);
  if (!node) {
    node = document.createElement('meta');
    document.head.appendChild(node);
  }
  Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
};

function RouteMetadata() {
  const location = useLocation();

  useEffect(() => {
    const metadata = PAGE_METADATA[location.pathname] || {
      title: DEFAULT_TITLE,
      description: DEFAULT_DESCRIPTION,
    };

    document.title = metadata.title;
    upsertMeta('meta[name="description"]', { name: 'description', content: metadata.description });
    upsertMeta('meta[property="og:title"]', { property: 'og:title', content: metadata.title });
    upsertMeta('meta[property="og:description"]', {
      property: 'og:description',
      content: metadata.description,
    });
    upsertMeta('meta[property="twitter:title"]', { property: 'twitter:title', content: metadata.title });
    upsertMeta('meta[property="twitter:description"]', {
      property: 'twitter:description',
      content: metadata.description,
    });
  }, [location.pathname]);

  return null;
}

const LoadingScreen = () => (
  <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center gap-4">
    <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
    <p className="text-sm font-semibold text-gray-700">Loading NeuroScreen...</p>
  </div>
);

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authWarning, setAuthWarning] = useState('');

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      let parsedUser = null;
      try {
        parsedUser = JSON.parse(storedUser);
      } catch {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setIsAuthenticated(false);
        setUser(null);
        setLoading(false);
        return;
      }

      try {
        // Verify token is still valid
        await authAPI.verify();
        setIsAuthenticated(true);
        setUser(parsedUser);
        setAuthWarning('');
      } catch (error) {
        if (error?.code === 'ERR_NETWORK' || error?.code === 'ECONNREFUSED') {
          // Preserve local session if backend is temporarily unreachable.
          setIsAuthenticated(true);
          setUser(parsedUser);
          setAuthWarning('Backend is temporarily unreachable. Some data may be outdated until connectivity is restored.');
          setLoading(false);
          return;
        }

        // Token invalid, clear storage
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setIsAuthenticated(false);
        setUser(null);
      }
    }
    setLoading(false);
  };

  const handleLogin = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setIsAuthenticated(true);
    setUser(userData);
    setAuthWarning('');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Router>
      <RouteMetadata />
      {authWarning ? (
        <div className="border-b border-amber-300 bg-amber-50 px-4 py-2 text-center text-sm font-semibold text-amber-800">
          {authWarning}
        </div>
      ) : null}
      <Suspense fallback={<LoadingScreen />}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/about" element={<About />} />
          <Route path="/how-it-works" element={<HowItWorks />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/faq" element={<FAQ />} />
          <Route path="/contact" element={<Contact />} />
          <Route
            path="/login"
            element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login onLogin={handleLogin} />
            }
          />
          <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />} />
          <Route
            path="/dashboard"
            element={
              isAuthenticated ? (
                <Dashboard user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/test"
            element={
              isAuthenticated ? <TestPage user={user} onLogout={handleLogout} /> : <Navigate to="/login" replace />
            }
          />
          <Route
            path="/profile"
            element={
              isAuthenticated ? <Profile user={user} onLogout={handleLogout} /> : <Navigate to="/login" replace />
            }
          />
          <Route
            path="/learning"
            element={
              isAuthenticated ? <Learning user={user} onLogout={handleLogout} /> : <Navigate to="/login" replace />
            }
          />
          <Route
            path="/bookings"
            element={
              isAuthenticated ? <Bookings user={user} onLogout={handleLogout} /> : <Navigate to="/login" replace />
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </Router>
  );
}

export default App;
