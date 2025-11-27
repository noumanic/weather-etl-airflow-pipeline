"""
Unit tests for data validation helper
"""
from unittest.mock import Mock
from datetime import date
from dags.helpers import validate_loaded_data


def make_mock_pg_hook_with_counts(record_count=1, null_temp=0, invalid_temp=0, invalid_humidity=0, bad_conv_count=0):
    cursor = Mock()
    cursor.fetchone.side_effect = [(record_count,), (null_temp,), (invalid_temp,), (invalid_humidity,)]
    cursor.fetchall.return_value = [()] * bad_conv_count
    conn = Mock()
    conn.cursor.return_value = cursor
    hook = Mock()
    hook.get_conn.return_value = conn
    return hook


def test_validate_loaded_data_pass():
    hook = make_mock_pg_hook_with_counts(1, 0, 0, 0, 0)
    passed, messages = validate_loaded_data(pg_hook=hook, target_date=date.today())
    assert passed is True
    assert messages == []


def test_validate_loaded_data_fail():
    hook = make_mock_pg_hook_with_counts(0, 1, 0, 0, 2)
    passed, messages = validate_loaded_data(pg_hook=hook, target_date=date.today())
    assert passed is False
    assert len(messages) >= 1

