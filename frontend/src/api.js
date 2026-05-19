const BASE = import.meta.env.VITE_API_URL || '';

function authHeaders() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function http(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...(options.headers || {}),
    },
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`HTTP ${response.status}: ${detail}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  trending: () => http('/api/movies/trending'),
  search: (q, page = 1) => http(`/api/movies/search?q=${encodeURIComponent(q)}&page=${page}`),
  details: (id) => http(`/api/movies/${id}`),

  register: (username, password) =>
    http('/api/auth/register', { method: 'POST', body: JSON.stringify({ username, password }) }),
  login: async (username, password) => {
    const body = new URLSearchParams({ username, password });
    const response = await fetch(`${BASE}/api/auth/login`, { method: 'POST', body });
    if (!response.ok) throw new Error('Invalid credentials');
    return response.json();
  },

  watchlist: () => http('/api/watchlist'),
  addToWatchlist: (movie) =>
    http('/api/watchlist', {
      method: 'POST',
      body: JSON.stringify({
        tmdb_id: movie.id,
        title: movie.title,
        poster_path: movie.poster_path,
      }),
    }),
  removeFromWatchlist: (tmdbId) => http(`/api/watchlist/${tmdbId}`, { method: 'DELETE' }),
};

export const posterUrl = (path) =>
  path ? `https://image.tmdb.org/t/p/w500${path}` : 'https://via.placeholder.com/500x750?text=No+Poster';
