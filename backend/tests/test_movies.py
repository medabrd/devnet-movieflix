import httpx
import respx

from app.config import settings


@respx.mock
def test_trending_uses_tmdb(client):
    respx.get(f"{settings.tmdb_base_url}/trending/movie/week").mock(
        return_value=httpx.Response(
            200,
            json={
                "page": 1,
                "total_pages": 1,
                "total_results": 1,
                "results": [
                    {
                        "id": 1,
                        "title": "Test Movie",
                        "overview": "An overview",
                        "poster_path": "/p.jpg",
                        "release_date": "2024-01-01",
                        "vote_average": 7.5,
                    }
                ],
            },
        )
    )

    response = client.get("/api/movies/trending")
    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["title"] == "Test Movie"
