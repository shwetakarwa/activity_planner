from __future__ import annotations

import math

import httpx


def geocode_city(
    city: str,
    hint_lat: float | None = None,
    hint_lon: float | None = None,
) -> tuple[float, float]:
    # If user included a state/country qualifier (e.g. "Dublin, CA"), trust it directly.
    if "," in city:
        resp = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "format": "json"},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results:
            raise ValueError(f"City not found: {city}")
        return results[0]["latitude"], results[0]["longitude"]

    # Ambiguous name — fetch multiple candidates and pick the closest to the hint.
    resp = httpx.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 5, "format": "json"},
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        raise ValueError(f"City not found: {city}")

    if hint_lat is not None and hint_lon is not None and len(results) > 1:
        best = min(
            results,
            key=lambda r: _haversine_miles(hint_lat, hint_lon, r["latitude"], r["longitude"]),
        )
    else:
        best = results[0]

    return best["latitude"], best["longitude"]


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def get_user_location(ip: str | None = None) -> tuple[float, float] | None:
    if not ip:
        return None
    try:
        resp = httpx.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            return None
        return float(data["latitude"]), float(data["longitude"])
    except Exception:
        return None


def find_nearby_cities(
    city: str,
    miles: int,
    hint_lat: float | None = None,
    hint_lon: float | None = None,
) -> list[str]:
    lat, lon = geocode_city(city, hint_lat=hint_lat, hint_lon=hint_lon)
    meters = miles * 1609.34
    query = f'[out:json];node["place"~"city|town"](around:{meters:.0f},{lat},{lon});out body;'
    resp = httpx.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": query},
        timeout=20,
        headers={"User-Agent": "FamilyActivityFinder/1.0"},
    )
    resp.raise_for_status()
    elements = resp.json().get("elements", [])
    nearby = sorted(
        [
            (e["tags"]["name"], _haversine_miles(lat, lon, e["lat"], e["lon"]))
            for e in elements
            if "name" in e.get("tags", {})
        ],
        key=lambda x: x[1],
    )
    seen = {city.lower()}
    result = [city]
    for name, _ in nearby:
        if name.lower() not in seen and len(result) < 5:
            seen.add(name.lower())
            result.append(name)
    return result
