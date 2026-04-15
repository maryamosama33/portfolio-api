import httpx

BASE_URL = "http://localhost:8000"

async def fetch(endpoint: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/{endpoint}")
            response.raise_for_status()
            data = response.json()
            return data["items"]
    except httpx.RequestError as e:
        print(f"API request failed: {e}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"API returned error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []