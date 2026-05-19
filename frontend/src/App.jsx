import { useState } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import Home from './pages/Home.jsx';
import Watchlist from './pages/Watchlist.jsx';
import Login from './pages/Login.jsx';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const navigate = useNavigate();

  const handleLogin = (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    navigate('/');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    navigate('/');
  };

  return (
    <div className="app">
      <nav className="navbar">
        <Link to="/" className="brand">🎬 MovieFlix devnet cicd demo</Link>
        <div className="nav-links">
          <Link to="/">Tendances</Link>
          {token && <Link to="/watchlist">Ma liste</Link>}
          {token ? (
            <button onClick={handleLogout}>Déconnexion</button>
          ) : (
            <Link to="/login">Connexion</Link>
          )}
        </div>
      </nav>
      <main className="content">
        <Routes>
          <Route path="/" element={<Home authenticated={!!token} />} />
          <Route path="/watchlist" element={<Watchlist />} />
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
        </Routes>
      </main>
    </div>
  );
}
