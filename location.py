from __future__ import annotations

import math

import httpx


def geocode_city(city: str) -> tuple[float, float]:
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


def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def find_nearby_cities(city: str, miles: int) -> list[str]:
    lat, lon = geocode_city(city)
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
