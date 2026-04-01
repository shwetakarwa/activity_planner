from datetime import datetime
from unittest.mock import MagicMock, patch

from app import find_nearby_cities, parse_date


def test_parse_date_this_sunday():
    result = parse_date("this Sunday")
    assert result is not None
    dt = datetime.strptime(result, "%Y-%m-%d")
    assert dt.weekday() == 6  # Sunday


def test_parse_date_explicit():
    result = parse_date("April 5 2026")
    assert result == "2026-04-05"


def test_parse_date_invalid():
    result = parse_date("xyzzy foo bar 999")
    assert result is None


def _mock_geo(lat=37.5, lon=-122.2):
    m = MagicMock()
    m.json.return_value = {"results": [{"latitude": lat, "longitude": lon}]}
    return m


def _mock_overpass(names):
    m = MagicMock()
    m.json.return_value = {
        "elements": [{"tags": {"name": n}, "lat": 37.48, "lon": -122.23} for n in names]
    }
    return m


def test_find_nearby_cities_includes_entered_city():
    with patch("httpx.get", return_value=_mock_geo()), \
         patch("httpx.post", return_value=_mock_overpass(["Redwood City"])):
        result = find_nearby_cities("San Carlos", 10)
    assert "San Carlos" in result


def test_find_nearby_cities_deduplicates():
    with patch("httpx.get", return_value=_mock_geo()), \
         patch("httpx.post", return_value=_mock_overpass(["San Carlos", "Redwood City"])):
        result = find_nearby_cities("San Carlos", 10)
    assert result.count("San Carlos") == 1
