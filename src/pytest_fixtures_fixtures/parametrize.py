"""Module for parametrizing tests from fixture files."""

import csv
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeAlias, TypeVar

import pytest

try:
    import yaml
except ImportError:
    yaml = None

F = TypeVar("F", bound=Callable[..., Any])
"""Type variable for callable objects.

Represents any callable that accepts variable arguments and returns any type.
Used for decorator type annotations to preserve the original function signature.
"""

FixtureData: TypeAlias = tuple[str, list[tuple], list[str] | None]
"""Type alias for parametrized test data extracted from fixture files.

This type represents the structure of data returned by fixture parsing functions.
It contains:

- `str`: The fixture file name or identifier
- `list[tuple]`: List of parameter tuples for each test case
- `list[str] | None`: Optional list of test IDs, or None for auto-generated IDs

Example:
    ```python
    # Example FixtureData for a CSV with columns: id,name,age
    fixture_data: FixtureData = (
        "users.csv",
        [("alice", "30"), ("bob", "25")],  # Parameter tuples
        ["test_alice", "test_bob"]          # Optional test IDs
    )
    ```
"""


def parametrize_from_fixture(  # noqa: C901
    fixture_name: str,
    *,
    file_format: str = "auto",
    encoding: str = "utf-8",
    fixtures_dir: str | Path | None = None,
    id_field: str | None = "id",
    **kwargs: Any,
) -> Callable[[F], F]:
    """
    Parametrize a test function using data from a fixture file.

    This decorator reads data from a fixture file and automatically applies
    pytest.mark.parametrize to the test function. It supports CSV, JSON, JSONL,
    and YAML file formats.

    Args:
        fixture_name: Path to the fixture file relative to the fixtures directory.
        file_format: File format ("csv", "json", "jsonl", "yaml", or "auto" to detect from extension).
        encoding: Text encoding to use when reading the file (default: "utf-8").
        fixtures_dir: Override the fixtures directory path. If None, defaults to "tests/fixtures/".
        id_field: The field name to use for test IDs. If None, no test IDs will be used. Defaults to "id".
        **kwargs: Additional arguments passed to pytest.mark.parametrize.

    Returns:
        A decorator that parametrizes the test function.

    Raises:
        ValueError: If the file format is unsupported or data format is invalid.
        FileNotFoundError: If the fixture file doesn't exist.
        ImportError: If a required library is not installed.

    Note:
        Test IDs can be specified using a special column (CSV) or key (JSON/JSONL/YAML).
        When present, these IDs are automatically used for test identification. User-provided
        'ids' parameter takes precedence over file-based IDs.

    Example:
        CSV file with custom IDs:
        ```csv
        id,value,expected
        test_case_1,a,b
        test_case_2,x,y
        ```

        JSON file with custom IDs:
        ```json
        [
            {"id": "test_case_1", "value": "a", "expected": "b"},
            {"id": "test_case_2", "value": "x", "expected": "y"}
        ]
        ```

        Usage:
        ```python
        @parametrize_from_fixture("data.csv")
        def test_something(value, expected):
            # Runs with test IDs: test_case_1, test_case_2
            assert value != expected
        ```

    """

    def decorator(og_test_func: F) -> F:  # noqa: C901, PLR0912
        fixtures_path = _get_fixtures_path(fixtures_dir)

        # Detect file format if auto
        detected_format = file_format
        if detected_format == "auto":
            suffix = Path(fixture_name).suffix.lower()
            if suffix == ".csv":
                detected_format = "csv"
            elif suffix == ".json":
                detected_format = "json"
            elif suffix == ".jsonl":
                detected_format = "jsonl"
            elif suffix in [".yaml", ".yml"]:
                detected_format = "yaml"
            else:
                raise ValueError(f"Cannot auto-detect format for file: {fixture_name}")

        # Read the fixture file
        fixture_path = fixtures_path / fixture_name
        if not fixture_path.exists():
            raise FileNotFoundError(f"Fixture {fixture_name} does not exist at {fixture_path}")

        # Parse based on format
        if detected_format == "csv":
            param_names, param_values, test_ids = _read_csv_for_parametrize(fixture_path, encoding, id_field)
        elif detected_format == "json":
            param_names, param_values, test_ids = _read_json_for_parametrize(fixture_path, encoding, id_field)
        elif detected_format == "jsonl":
            param_names, param_values, test_ids = _read_jsonl_for_parametrize(fixture_path, encoding, id_field)
        elif detected_format == "yaml":
            param_names, param_values, test_ids = _read_yaml_for_parametrize(fixture_path, encoding, id_field)
        else:
            raise ValueError(f"Unsupported file format: {detected_format}")

        # Apply parametrize with the data
        parametrize_kwargs = {"argnames": param_names, "argvalues": param_values, **kwargs}

        # Use extracted test IDs if available and not overridden by user
        if test_ids is not None and "ids" not in kwargs:
            parametrize_kwargs["ids"] = test_ids

        return pytest.mark.parametrize(**parametrize_kwargs)(og_test_func)

    return decorator


def _get_fixtures_path(fixtures_dir: str | Path | None = None) -> Path:
    """Get the fixtures directory path."""
    if fixtures_dir is not None:
        return Path(fixtures_dir).resolve()

    env_path = os.environ.get("PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE")
    if env_path:
        return Path(env_path).resolve()

    # Default path relative to current working directory
    return Path.cwd() / "tests" / "fixtures"


def _read_csv_for_parametrize(file_path: Path, encoding: str, id_field: str | None = "id") -> FixtureData:
    """Read CSV file and return parameter names, values, and optional test IDs for parametrize."""
    with open(file_path, encoding=encoding) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError(f"CSV file {file_path} has no headers")

        rows = list(reader)
        if not rows:
            raise ValueError(f"CSV file {file_path} has no data rows")

        # Check if there's an 'id' column for test IDs
        test_ids = None
        if id_field in fieldnames:
            test_ids = [row[id_field] for row in rows]
            # Remove 'id' from fieldnames and data
            fieldnames = [field for field in fieldnames if field != id_field]

        # Convert dict rows to tuples in field order (excluding 'id')
        param_values = [tuple(row[field] for field in fieldnames) for row in rows]
        param_names = ",".join(fieldnames)

        return param_names, param_values, test_ids


def _read_json_for_parametrize(file_path: Path, encoding: str, id_field: str | None = "id") -> FixtureData:
    """Read JSON file and return parameter names, values, and optional test IDs for parametrize."""
    with open(file_path, encoding=encoding) as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"JSON file {file_path} must contain a list of objects")

    if not data:
        raise ValueError(f"JSON file {file_path} contains empty list")

    # Get parameter names from the first object's keys
    first_item = data[0]
    if not isinstance(first_item, dict):
        raise ValueError(f"JSON file {file_path} must contain a list of dictionaries")

    fieldnames = list(first_item.keys())

    # Check if there's an 'id' key for test IDs
    test_ids = None
    if id_field in fieldnames:
        test_ids = [str(item[id_field]) for item in data]
        # Remove 'id' from fieldnames
        fieldnames = [field for field in fieldnames if field != id_field]

    param_names = ",".join(fieldnames)

    # Convert each dict to a tuple in field order (excluding 'id')
    param_values = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"All items in JSON file {file_path} must be dictionaries")
        expected_keys = set(fieldnames)
        if id_field in item:
            expected_keys.add(id_field)
        if set(item.keys()) != expected_keys:
            raise ValueError(f"All items in JSON file {file_path} must have the same keys")
        param_values.append(tuple(item[field] for field in fieldnames))

    return param_names, param_values, test_ids


def _read_jsonl_for_parametrize(file_path: Path, encoding: str, id_field: str | None = "id") -> FixtureData:
    """Read JSONL file and return parameter names, values, and optional test IDs for parametrize."""
    data = []
    with open(file_path, encoding=encoding) as f:
        for line in f:
            clean_line = line.strip()
            if clean_line:  # Skip empty lines
                data.append(json.loads(clean_line))

    if not data:
        raise ValueError(f"JSONL file {file_path} contains no data")

    # Get parameter names from the first object's keys
    first_item = data[0]
    if not isinstance(first_item, dict):
        raise ValueError(f"JSONL file {file_path} must contain dictionaries")

    fieldnames = list(first_item.keys())

    # Check if there's an 'id' key for test IDs
    test_ids = None
    if id_field in fieldnames:
        test_ids = [str(item[id_field]) for item in data]
        # Remove 'id' from fieldnames
        fieldnames = [field for field in fieldnames if field != id_field]

    param_names = ",".join(fieldnames)

    # Convert each dict to a tuple in field order (excluding 'id')
    param_values = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"All items in JSONL file {file_path} must be dictionaries")
        expected_keys = set(fieldnames)
        if id_field in item:
            expected_keys.add(id_field)
        if set(item.keys()) != expected_keys:
            raise ValueError(f"All items in JSONL file {file_path} must have the same keys")
        param_values.append(tuple(item[field] for field in fieldnames))

    return param_names, param_values, test_ids


def _read_yaml_for_parametrize(file_path: Path, encoding: str, id_field: str | None = "id") -> FixtureData:
    """Read YAML file and return parameter names, values, and optional test IDs for parametrize."""
    if yaml is None:
        raise ImportError("PyYAML is required for YAML fixtures. Install it: https://pypi.org/project/PyYAML/")

    with open(file_path, encoding=encoding) as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

    if not isinstance(data, list):
        raise ValueError(f"YAML file {file_path} must contain a list of objects")

    if not data:
        raise ValueError(f"YAML file {file_path} contains empty list")

    # Get parameter names from the first object's keys
    first_item = data[0]
    if not isinstance(first_item, dict):
        raise ValueError(f"YAML file {file_path} must contain a list of dictionaries")

    fieldnames = list(first_item.keys())

    # Check if there's an 'id' key for test IDs
    test_ids = None
    if id_field in fieldnames:
        test_ids = [str(item[id_field]) for item in data]
        # Remove 'id' from fieldnames
        fieldnames = [field for field in fieldnames if field != id_field]

    param_names = ",".join(fieldnames)

    # Convert each dict to a tuple in field order (excluding 'id')
    param_values = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"All items in YAML file {file_path} must be dictionaries")
        expected_keys = set(fieldnames)
        if id_field in item:
            expected_keys.add(id_field)
        if set(item.keys()) != expected_keys:
            raise ValueError(f"All items in YAML file {file_path} must have the same keys")
        param_values.append(tuple(item[field] for field in fieldnames))

    return param_names, param_values, test_ids
