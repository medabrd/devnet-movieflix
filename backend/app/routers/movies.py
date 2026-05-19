from fastapi import APIRouter, Depends, Query

from app.schemas import MovieList, MovieSummary
from app.services.tmdb import TMDBClient, get_tmdb_client

router = APIRouter(prefix="/api/movies", tags=["movies"])


def _summary(raw: dict) -> MovieSummary:
    return MovieSummary(
        id=raw["id"],
        title=raw.get("title") or raw.get("name") or "Untitled",
        overview=raw.get("overview"),
        poster_path=raw.get("poster_path"),
        release_date=raw.get("release_date"),
        vote_average=raw.get("vote_average"),
    )


@router.get("/trending", response_model=MovieList)
async def trending(tmdb: TMDBClient = Depends(get_tmdb_client)):
    data = await tmdb.trending()
    return MovieList(
        page=data.get("page", 1),
        total_pages=data.get("total_pages", 1),
        total_results=data.get("total_results", 0),
        results=[_summary(m) for m in data.get("results", [])],
    )


@router.get("/search", response_model=MovieList)
async def search(
    q: str = Query(min_length=1),
    page: int = Query(default=1, ge=1, le=500),
    tmdb: TMDBClient = Depends(get_tmdb_client),
):
    data = await tmdb.search(q, page)
    return MovieList(
        page=data.get("page", 1),
        total_pages=data.get("total_pages", 1),
        total_results=data.get("total_results", 0),
        results=[_summary(m) for m in data.get("results", [])],
    )


@router.get("/{movie_id}", response_model=MovieSummary)
async def details(movie_id: int, tmdb: TMDBClient = Depends(get_tmdb_client)):
    data = await tmdb.details(movie_id)
    return _summary(data)
