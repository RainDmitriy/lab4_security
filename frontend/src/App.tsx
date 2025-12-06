import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuthState } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import NewsDetail from './pages/NewsDetail';
import Login from './pages/Login';
import Register from './pages/Register';
import CreateNews from './pages/NewsCreate';
import EditNews from './pages/NewsEdit';

// --- Protected Route ---

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuthState();
  return user ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <Navbar />
        <div style={{ padding: '1rem' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/news/:id" element={<NewsDetail />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} /> {}
            <Route path="/create-news" element={<ProtectedRoute><CreateNews /></ProtectedRoute>} />
            <Route path="/edit-news/:id" element={<ProtectedRoute><EditNews /></ProtectedRoute>} />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
};

export default App;