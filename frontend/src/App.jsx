/**
 * App - Main application component with routing
 */
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import AdminDashboard from './pages/AdminDashboard';
import PageTransition from './components/PageTransition';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<PageTransition key="home"><HomePage /></PageTransition>} />
        <Route path="/chat" element={<PageTransition key="chat"><ChatPage /></PageTransition>} />
        <Route path="/admin" element={<PageTransition key="admin"><AdminDashboard /></PageTransition>} />
      </Routes>
    </Router>
  );
}

export default App;
