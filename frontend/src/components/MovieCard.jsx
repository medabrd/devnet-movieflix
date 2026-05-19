import { posterUrl } from '../api.js';

export default function MovieCard({ movie, onAdd, onRemove, action }) {
  return (
    <article className="card">
      <img src={posterUrl(movie.poster_path)} alt={movie.title} loading="lazy" />
      <div className="card-body">
        <h3>{movie.title}</h3>
        {movie.vote_average !== undefined && (
          <span className="rating">⭐ {Number(movie.vote_average ?? 0).toFixed(1)}</span>
        )}
        {action === 'add' && onAdd && <button onClick={() => onAdd(movie)}>+ Watchlist</button>}
        {action === 'remove' && onRemove && (
          <button className="danger" onClick={() => onRemove(movie.tmdb_id ?? movie.id)}>
            Retirer
          </button>
        )}
      </div>
    </article>
  );
}
