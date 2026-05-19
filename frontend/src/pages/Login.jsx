import { useState } from 'react';
import { api } from '../api.js';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [mode, setMode] = useState('login');
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    try {
      const result = mode === 'login'
        ? await api.login(username, password)
        : await api.register(username, password);
      onLogin(result.access_token);
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="auth-card">
      <h2>{mode === 'login' ? 'Connexion' : 'Créer un compte'}</h2>
      <form onSubmit={handleSubmit}>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Nom d'utilisateur"
          required
          minLength={3}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Mot de passe"
          required
          minLength={6}
        />
        <button type="submit">{mode === 'login' ? 'Se connecter' : "S'inscrire"}</button>
      </form>
      {error && <p className="error">{error}</p>}
      <button className="link" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
        {mode === 'login' ? "Pas de compte ? S'inscrire" : 'Déjà inscrit ? Se connecter'}
      </button>
    </div>
  );
}
