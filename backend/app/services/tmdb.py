import httpx
from fastapi import HTTPException

from app.config import settings


class TMDBClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.tmdb_api_key
        self.base_url = base_url or settings.tmdb_base_url

    async def _get(self, path: str, params: dict | None = None) -> dict:
        params = {**(params or {}), "api_key": self.api_key, "language": "fr-FR"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.base_url}{path}", params=params)
            except httpx.HTTPError as exc:
                raise HTTPException(status_code=502, detail=f"TMDB unreachable: {exc}") from exc

        if response.status_code == 401:
            raise HTTPException(status_code=502, detail="TMDB authentication failed (check API key)")
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

    async def trending(self, window: str = "week") -> dict:
        return await self._get(f"/trending/movie/{window}")

    async def search(self, query: str, page: int = 1) -> dict:
        return await self._get("/search/movie", {"query": query, "page": page})

    async def details(self, movie_id: int) -> dict:
        return await self._get(f"/movie/{movie_id}")


def get_tmdb_client() -> TMDBClient:
    return TMDBClient()
