from datetime import datetime
from unittest.mock import MagicMock, patch

import httpx

from app import parse_date
from location import find_nearby_cities, geocode_city, get_user_location


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


def _mock_geo_multi(results):
    """results is a list of (lat, lon) tuples."""
    m = MagicMock()
    m.json.return_value = {
        "results": [{"latitude": lat, "longitude": lon} for lat, lon in results]
    }
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


# --- geocode_city disambiguation tests ---

def test_geocode_city_explicit_qualifier_skips_hint():
    # "Dublin, CA" has a comma — should use count=1 and return results[0] without hint logic.
    mock = _mock_geo(lat=37.7, lon=-121.9)
    with patch("httpx.get", return_value=mock) as mock_get:
        lat, lon = geocode_city("Dublin, CA", hint_lat=53.3, hint_lon=-6.3)
    call_params = mock_get.call_args[1]["params"]
    assert call_params["count"] == 1
    assert lat == 37.7
    assert lon == -121.9


def test_geocode_city_uses_hint_to_pick_closest():
    # Two candidates: Dublin CA (~37.7, -121.9) and Dublin IE (~53.3, -6.3).
    # Bay Area hint (37.5, -122.0) should pick Dublin CA.
    mock = _mock_geo_multi([(37.7, -121.9), (53.3, -6.3)])
    with patch("httpx.get", return_value=mock):
        lat, lon = geocode_city("Dublin", hint_lat=37.5, hint_lon=-122.0)
    assert abs(lat - 37.7) < 1.0
    assert lon < 0  # Western hemisphere = CA, not Ireland


def test_geocode_city_no_hint_uses_first_result():
    # No hint — should fall back to results[0].
    mock = _mock_geo_multi([(53.3, -6.3), (37.7, -121.9)])
    with patch("httpx.get", return_value=mock):
        lat, lon = geocode_city("Dublin")
    assert abs(lat - 53.3) < 0.1


def test_geocode_city_single_result_ignores_hint():
    # Only one result — hint should not cause any errors.
    mock = _mock_geo(lat=37.5, lon=-122.2)
    with patch("httpx.get", return_value=mock):
        lat, lon = geocode_city("San Carlos", hint_lat=0.0, hint_lon=0.0)
    assert lat == 37.5
    assert lon == -122.2


def test_find_nearby_cities_passes_hint_through():
    # Hint coordinates should be accepted and city should still be in result.
    with patch("httpx.get", return_value=_mock_geo()), \
         patch("httpx.post", return_value=_mock_overpass(["Redwood City"])):
        result = find_nearby_cities("Dublin", 10, hint_lat=37.5, hint_lon=-122.0)
    assert "Dublin" in result


# --- get_user_location tests ---

def test_get_user_location_success():
    mock = MagicMock()
    mock.json.return_value = {"latitude": 37.5, "longitude": -122.2}
    with patch("httpx.get", return_value=mock):
        result = get_user_location("1.2.3.4")
    assert result == (37.5, -122.2)


def test_get_user_location_none_ip():
    with patch("httpx.get") as mock_get:
        result = get_user_location(None)
    assert result is None
    mock_get.assert_not_called()


def test_get_user_location_empty_ip():
    with patch("httpx.get") as mock_get:
        result = get_user_location("")
    assert result is None
    mock_get.assert_not_called()


def test_get_user_location_error_response():
    mock = MagicMock()
    mock.json.return_value = {"error": True, "reason": "Reserved IP Address"}
    with patch("httpx.get", return_value=mock):
        result = get_user_location("192.168.1.1")
    assert result is None


def test_get_user_location_network_failure():
    with patch("httpx.get", side_effect=httpx.RequestError("timeout")):
        result = get_user_location("1.2.3.4")
    assert result is None
