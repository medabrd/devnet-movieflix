from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MovieSummary(BaseModel):
    id: int
    title: str
    overview: str | None = None
    poster_path: str | None = None
    release_date: str | None = None
    vote_average: float | None = None


class MovieList(BaseModel):
    page: int
    total_pages: int
    total_results: int
    results: list[MovieSummary]


class WatchlistAdd(BaseModel):
    tmdb_id: int
    title: str
    poster_path: str | None = None


class WatchlistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tmdb_id: int
    title: str
    poster_path: str | None = None
    added_at: datetime
