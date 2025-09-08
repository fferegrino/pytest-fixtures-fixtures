"""Tests for parametrize_from_fixture decorator."""

from pytest_fixtures_fixtures.parametrize import parametrize_from_fixture


def assert_all_ints(*value):
    assert all(isinstance(v, int) for v in value)


@parametrize_from_fixture("test_data.csv")
def test_sum_three_numbers_csv(a, b, c):
    assert int(a) + int(b) == int(c)


@parametrize_from_fixture("test_data.csv", file_format="csv")
def test_explicit_format(a, b, c):
    """Test parametrization with explicit file format."""
    assert int(a) + int(b) == int(c)


@parametrize_from_fixture("test_data.json")
def test_sum_three_numbers_json(a, b, c):
    """Test parametrization from JSON file."""
    assert_all_ints(a, b, c)
    assert a + b == c


@parametrize_from_fixture("test_data.yaml")
def test_sum_three_numbers_yaml(a, b, c):
    """Test parametrization from YAML file."""
    # This test should run with Alice/30, Bob/25, Charlie/35
    assert_all_ints(a, b, c)
    assert a + b == c


@parametrize_from_fixture("test_data.jsonl")
def test_sum_three_numbers_jsonl(a, b, c):
    """Test parametrization from JSONL file."""
    # This test should run with alice/login, bob/logout, charlie/login
    assert_all_ints(a, b, c)
    assert a + b == c
