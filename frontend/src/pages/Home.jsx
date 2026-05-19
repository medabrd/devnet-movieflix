import { useEffect, useState } from 'react';
import { api } from '../api.js';
import MovieCard from '../components/MovieCard.jsx';

export default function Home({ authenticated }) {
  const [query, setQuery] = useState('');
  const [movies, setMovies] = useState([]);
  const [title, setTitle] = useState('Tendances de la semaine');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api
      .trending()
      .then((data) => setMovies(data.results))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleSearch = async (event) => {
    event.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.search(query);
      setMovies(data.results);
      setTitle(`Résultats pour "${query}"`);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (movie) => {
    try {
      await api.addToWatchlist(movie);
      alert(`"${movie.title}" ajouté à votre watchlist`);
    } catch (e) {
      alert(e.message);
    }
  };

  return (
    <div>
      <form onSubmit={handleSearch} className="search-form">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Rechercher un film..."
        />
        <button type="submit">Rechercher</button>
      </form>
      <h2>{title}</h2>
      {error && <p className="error">{error}</p>}
      {loading && <p>Chargement...</p>}
      <div className="grid">
        {movies.map((m) => (
          <MovieCard
            key={m.id}
            movie={m}
            action={authenticated ? 'add' : undefined}
            onAdd={handleAdd}
          />
        ))}
      </div>
    </div>
  );
}
