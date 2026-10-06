/**
 * App - Main application component with routing
 */
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import AdminDashboard from './pages/AdminDashboard';
import LoginPage from './pages/LoginPage';
import PageTransition from './components/PageTransition';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<PageTransition key="home"><HomePage /></PageTransition>} />
          <Route path="/chat" element={<PageTransition key="chat"><ChatPage /></PageTransition>} />
          <Route path="/admin/login" element={<PageTransition key="admin-login"><LoginPage /></PageTransition>} />
          <Route path="/admin" element={<PageTransition key="admin"><AdminDashboard /></PageTransition>} />
          <Route path="/admin/dashboard" element={<PageTransition key="admin-dashboard"><AdminDashboard /></PageTransition>} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
