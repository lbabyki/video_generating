from app.api.errors import error_body


def test_error_response_is_standardized() -> None:
    assert error_body("VALIDATION_ERROR", "Request validation failed") == {
        "error": {"code": "VALIDATION_ERROR", "message": "Request validation failed"}
    }
