import { useEffect, useState } from 'react';
import { api } from '../api.js';
import MovieCard from '../components/MovieCard.jsx';

export default function Watchlist() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);

  const refresh = () => {
    api
      .watchlist()
      .then(setItems)
      .catch((e) => setError(e.message));
  };

  useEffect(refresh, []);

  const handleRemove = async (tmdbId) => {
    await api.removeFromWatchlist(tmdbId);
    refresh();
  };

  return (
    <div>
      <h2>Ma watchlist</h2>
      {error && <p className="error">{error}</p>}
      {items.length === 0 && <p>Aucun film dans votre liste.</p>}
      <div className="grid">
        {items.map((item) => (
          <MovieCard key={item.id} movie={item} action="remove" onRemove={handleRemove} />
        ))}
      </div>
    </div>
  );
}
