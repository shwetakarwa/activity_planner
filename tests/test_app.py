from app import DUMMY_ACTIVITIES, render_card, validate_inputs

REQUIRED_KEYS = {"emoji", "title", "description", "location", "distance"}


def test_dummy_activities_count():
    assert len(DUMMY_ACTIVITIES) == 5


def test_dummy_activities_have_required_keys():
    for activity in DUMMY_ACTIVITIES:
        missing = REQUIRED_KEYS - activity.keys()
        assert not missing, f"Activity missing keys: {missing}"


def test_dummy_activities_no_empty_fields():
    for activity in DUMMY_ACTIVITIES:
        for key in REQUIRED_KEYS:
            assert activity[key].strip(), f"Activity has empty '{key}'"


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
