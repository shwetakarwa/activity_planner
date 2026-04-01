from app import validate_inputs


def test_validate_inputs_all_valid():
    assert validate_inputs("San Carlos", "2 years", "Sunday afternoon") == []


def test_validate_inputs_all_empty():
    errors = validate_inputs("", "", "")
    assert len(errors) == 3


def test_validate_inputs_whitespace_only():
    errors = validate_inputs("  ", "  ", "  ")
    assert len(errors) == 3


def test_validate_inputs_partial():
    errors = validate_inputs("San Carlos", "", "")
    assert len(errors) == 2
    assert any("Ages" in e for e in errors)
    assert any("Availability" in e for e in errors)
