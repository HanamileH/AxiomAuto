import datetime as dt


from app.db.connection import _json_safe, _sql_operation


def test_connection_utils_sql_operation_and_json_safe():
    assert _sql_operation("-- comment\nSELECT 1;") == "SELECT"
    assert (
        _sql_operation(
            """
            WITH q AS (SELECT 1)
            UPDATE users SET role = 'admin' WHERE id = 1;
            """
        )
        == "UPDATE"
    )

    payload = {
        "b": b"\xff",
        "d": dt.datetime(2026, 5, 11, 12, 0, 0, tzinfo=dt.timezone.utc),
        "n": None,
        "nested": {"x": [1, True, b"ok"]},
    }
    normalized = _json_safe(payload)
    assert normalized["n"] is None
    assert normalized["d"].endswith("+00:00")
    assert isinstance(normalized["b"], str)
    assert normalized["nested"]["x"][2] == "ok"

