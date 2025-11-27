"""
Unit tests for extract helper
"""
import json
from unittest.mock import patch, Mock
from dags.helpers import call_open_meteo_api


SAMPLE_API_RESPONSE = {
    "current_weather": {
        "temperature": 15.0,
        "windspeed": 5.0,
        "weathercode": 0,
        "time": "2024-01-01T12:00:00Z",
    },
    "hourly": {
        "time": ["2024-01-01T12:00:00Z"],
        "relativehumidity_2m": [55.0]
    }
}


def make_mock_get():
    m = Mock()
    m.return_value.status_code = 200
    m.return_value.json.return_value = SAMPLE_API_RESPONSE
    return m


def test_call_open_meteo_api_success(monkeypatch):
    mock_get = make_mock_get()
    monkeypatch.setattr("requests.get", mock_get)

    city = {"name": "Test", "latitude": 0.0, "longitude": 0.0}
    rec = call_open_meteo_api(city)
    assert rec["city"] == "Test"
    assert rec["temperature_celsius"] == 15.0
    assert rec["humidity"] == 55.0
    assert rec["timestamp"] == "2024-01-01T12:00:00Z"
