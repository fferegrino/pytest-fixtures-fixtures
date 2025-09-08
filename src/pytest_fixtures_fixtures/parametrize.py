"""Module for parametrizing tests from fixture files."""

import csv
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

import pytest

try:
    import yaml
except ImportError:
    yaml = None

F = TypeVar("F", bound=Callable[..., Any])


def parametrize_from_fixture(  # noqa: C901
    fixture_name: str,
    *,
    file_format: str = "auto",
    encoding: str = "utf-8",
    fixtures_dir: str | Path | None = None,
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
        **kwargs: Additional arguments passed to pytest.mark.parametrize.

    Returns:
        A decorator that parametrizes the test function.

    Raises:
        ValueError: If the file format is unsupported or data format is invalid.
        FileNotFoundError: If the fixture file doesn't exist.
        ImportError: If a required library is not installed.

    """

    def decorator(og_test_func: F) -> F:  # noqa: C901
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
            param_names, param_values = _read_csv_for_parametrize(fixture_path, encoding)
        elif detected_format == "json":
            param_names, param_values = _read_json_for_parametrize(fixture_path, encoding)
        elif detected_format == "jsonl":
            param_names, param_values = _read_jsonl_for_parametrize(fixture_path, encoding)
        elif detected_format == "yaml":
            param_names, param_values = _read_yaml_for_parametrize(fixture_path, encoding)
        else:
            raise ValueError(f"Unsupported file format: {detected_format}")

        # Apply parametrize with the data
        parametrize_kwargs = {"argnames": param_names, "argvalues": param_values, **kwargs}
        return pytest.mark.parametrize(**parametrize_kwargs)(og_test_func)

    return decorator


def _get_fixtures_path(fixtures_dir: str | Path | None = None) -> Path:
    """Get the fixtures directory path."""
    # TODO: use fixtures_dir if provided
    # Default path relative to current working directory
    return Path.cwd() / "tests" / "fixtures"


def _read_csv_for_parametrize(file_path: Path, encoding: str) -> tuple[str, list[tuple]]:
    """Read CSV file and return parameter names and values for parametrize."""
    with open(file_path, encoding=encoding) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError(f"CSV file {file_path} has no headers")

        rows = list(reader)
        if not rows:
            raise ValueError(f"CSV file {file_path} has no data rows")

        # Convert dict rows to tuples in field order
        param_values = [tuple(row[field] for field in fieldnames) for row in rows]
        param_names = ",".join(fieldnames)

        return param_names, param_values


def _read_json_for_parametrize(file_path: Path, encoding: str) -> tuple[str, list[tuple]]:
    """Read JSON file and return parameter names and values for parametrize."""
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
    param_names = ",".join(fieldnames)

    # Convert each dict to a tuple in field order
    param_values = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"All items in JSON file {file_path} must be dictionaries")
        if set(item.keys()) != set(fieldnames):
            raise ValueError(f"All items in JSON file {file_path} must have the same keys")
        param_values.append(tuple(item[field] for field in fieldnames))

    return param_names, param_values


def _read_jsonl_for_parametrize(file_path: Path, encoding: str) -> tuple[str, list[tuple]]:
    """Read JSONL file and return parameter names and values for parametrize."""
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
    param_names = ",".join(fieldnames)

    # Convert each dict to a tuple in field order
    param_values = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"All items in JSONL file {file_path} must be dictionaries")
        if set(item.keys()) != set(fieldnames):
            raise ValueError(f"All items in JSONL file {file_path} must have the same keys")
        param_values.append(tuple(item[field] for field in fieldnames))

    return param_names, param_values


def _read_yaml_for_parametrize(file_path: Path, encoding: str) -> tuple[str, list[tuple]]:
    """Read YAML file and return parameter names and values for parametrize."""
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
    param_names = ",".join(fieldnames)

    # Convert each dict to a tuple in field order
    param_values = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"All items in YAML file {file_path} must be dictionaries")
        if set(item.keys()) != set(fieldnames):
            raise ValueError(f"All items in YAML file {file_path} must have the same keys")
        param_values.append(tuple(item[field] for field in fieldnames))

    return param_names, param_values
