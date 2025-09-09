"""Module containing pytest fixtures."""

import csv
import json
import os
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

import pytest


def pytest_configure(config: pytest.Config):
    """Configure pytest plugin."""


def pytest_addoption(parser: pytest.Parser):
    """Add pytest options."""
    parser.addoption(
        "--fixtures-fixtures-path",
        action="store",
        default=None,
        help="Path to the fixtures directory. Overrides the default 'tests/fixtures/' path.",
    )


@pytest.fixture
def fixtures_path(pytestconfig, request):
    """
    Get the path to the test fixtures directory.

    This fixture provides a Path object pointing to the test fixtures directory.
    By default, it uses `tests/fixtures/` relative to the project root.

    The fixture directory can be customized in several ways:
    1. Command line: pytest --fixtures-fixtures-path=path/to/fixtures
    2. pytest.ini: addopts = --fixtures-fixtures-path=path/to/fixtures
    3. pyproject.toml: addopts = "--fixtures-fixtures-path=path/to/fixtures"
    4. Override this fixture in your tests for programmatic control

    Args:
        pytestconfig: The pytest configuration object.
        request: The pytest request object.

    Returns:
        Path: A pathlib.Path object pointing to the fixtures directory.

    Example:
        Basic usage in a test function:
        
        ```python
        def test_something(fixtures_path):
            assert fixtures_path.exists()
            assert fixtures_path.name == "fixtures"
        ```

    """
    fixtures_path = pytestconfig.getoption("fixtures_fixtures_path")
    if fixtures_path:
        return Path(fixtures_path).resolve()
    return Path(pytestconfig.rootdir) / "tests" / "fixtures"


@pytest.fixture
def path_for_fixture(fixtures_path):
    """
    Get a Path object for a specific fixture file.

    This fixture returns a function that constructs paths to fixture files
    within the fixtures directory. It can optionally validate that the
    fixture file exists.

    Args:
        fixtures_path: The path to the fixtures directory.

    Returns:
        Callable: A function that takes fixture name components and returns a Path.

    The returned function accepts:
        *fixture_name: Components of the fixture file path (e.g., "data", "sample.json")
        must_exist: If True, raises FileNotFoundError if the fixture doesn't exist.

    Returns:
        Path: A pathlib.Path object pointing to the fixture file.

    Raises:
        FileNotFoundError: If must_exist=True and the fixture file doesn't exist.

    Example:
        Getting a path to a fixture file:
        
        ```python
        def test_data_file(path_for_fixture):
            data_path = path_for_fixture("data", "sample.json")
            assert data_path.suffix == ".json"
        ```
        
        Working with optional fixtures that may not exist:
        
        ```python
        def test_optional_fixture(path_for_fixture):
            # Won't raise error if file doesn't exist
            path = path_for_fixture("optional", "file.txt", must_exist=False)
        ```

    """

    def _path_for_fixture(*fixture_name: str | os.PathLike[str], must_exist: bool = True) -> Path:
        fixture_name = Path(*fixture_name)
        path = fixtures_path / fixture_name
        if must_exist and not path.exists():
            raise FileNotFoundError(f"Fixture {fixture_name} does not exist")
        return path

    return _path_for_fixture


@pytest.fixture
def read_fixture(path_for_fixture):
    r"""
    Read and optionally deserialize a fixture file.

    This fixture returns a function that reads fixture files with customizable
    encoding, file mode, and deserialization. It's the base fixture for
    reading any type of fixture file.

    Args:
        path_for_fixture: Function to get paths to fixture files.

    Returns:
        Callable: A function that reads and optionally processes fixture files.

    The returned function accepts:
        *fixture_name: Components of the fixture file path.
        encoding: Text encoding to use when reading the file (default: "utf-8").
        mode: File open mode (default: "r" for text mode).
        deserialize: Function to process the file contents (default: identity).

    Returns:
        Any: The result of applying the deserialize function to the file contents.

    Example:
        Reading a text fixture file:
        
        ```python
        def test_text_fixture(read_fixture):
            content = read_fixture("data", "sample.txt")
            assert "hello" in content
        ```
        
        Reading a binary fixture file:
        
        ```python
        def test_binary_fixture(read_fixture):
            data = read_fixture("data", "image.png", mode="rb", deserialize=lambda x: x)
            assert data.startswith(b'\x89PNG')
        ```

    """

    def _read_fixture(
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
        mode: str = "r",
        deserialize: Callable = lambda x: x,
    ) -> str:
        path = path_for_fixture(*fixture_name)
        # Don't pass encoding for binary modes
        if "b" in mode:
            with open(path, mode) as f:
                return deserialize(f.read())
        else:
            with open(path, mode, encoding=encoding) as f:
                return deserialize(f.read())

    return _read_fixture


@pytest.fixture
def read_json_fixture(read_fixture):
    """
    Read and parse a JSON fixture file.

    This fixture returns a function that reads JSON fixture files and
    automatically parses them into Python dictionaries.

    Args:
        read_fixture: The base fixture reading function.

    Returns:
        Callable: A function that reads and parses JSON fixture files.

    The returned function accepts:
        *fixture_name: Components of the JSON fixture file path.
        must_exist: If True, raises FileNotFoundError if the fixture doesn't exist.
        encoding: Text encoding to use when reading the file (default: "utf-8").

    Returns:
        dict: The parsed JSON data as a Python dictionary.

    Raises:
        FileNotFoundError: If must_exist=True and the fixture file doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.

    Example:
        Reading a configuration JSON file:
        
        ```python
        def test_config_data(read_json_fixture):
            config = read_json_fixture("config", "settings.json")
            assert config["database"]["host"] == "localhost"
        ```
        
        Reading user data from a JSON file:
        
        ```python
        def test_user_data(read_json_fixture):
            users = read_json_fixture("data", "users.json")
            assert len(users["users"]) > 0
        ```

    """

    def _read_json_fixture(
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
    ) -> dict:
        return read_fixture(*fixture_name, encoding=encoding, deserialize=json.loads)

    return _read_json_fixture


@pytest.fixture
def read_jsonl_fixture(path_for_fixture):
    """
    Read and parse a JSONL (JSON Lines) fixture file.

    This fixture returns a function that reads JSONL fixture files, where
    each line contains a separate JSON object. The result is a generator of
    dictionaries, one for each line in the file, allowing for memory-efficient
    processing of large files.

    Args:
        path_for_fixture: Function to get paths to fixture files.

    Returns:
        Callable: A function that reads and parses JSONL fixture files.

    The returned function accepts:
        *fixture_name: Components of the JSONL fixture file path.
        encoding: Text encoding to use when reading the file (default: "utf-8").

    Returns:
        Generator[dict, None, None]: A generator of dictionaries, one for each JSON object in the file.

    Raises:
        FileNotFoundError: If the fixture file doesn't exist.
        json.JSONDecodeError: If any line contains invalid JSON.

    Example:
        Reading log entries from a JSONL file:
        
        ```python
        def test_log_entries(read_jsonl_fixture):
            logs = read_jsonl_fixture("logs", "access.jsonl")
            first_log = next(logs)
            assert "timestamp" in first_log
        ```
        
        Processing user records from a JSONL file:
        
        ```python
        def test_user_records(read_jsonl_fixture):
            users = read_jsonl_fixture("data", "users.jsonl")
            assert all("id" in user for user in users)
        ```

    """

    def _read_jsonl_fixture(
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
    ) -> Generator[dict, None, None]:
        path = path_for_fixture(*fixture_name)
        with open(path, encoding=encoding) as f:
            for line in f:
                clean_line = line.strip()
                if clean_line:  # Skip empty lines
                    yield json.loads(clean_line)

    return _read_jsonl_fixture


@pytest.fixture
def read_csv_fixture(path_for_fixture):
    """
    Read and parse a CSV fixture file.

    This fixture returns a function that reads CSV fixture files using
    Python's built-in csv.reader. The result is a generator of lists,
    one for each row in the file, allowing for memory-efficient
    processing of large CSV files. Each row is returned as a list of strings.

    Args:
        path_for_fixture: Function to get paths to fixture files.

    Returns:
        Callable: A function that reads and parses CSV fixture files.

    The returned function accepts:
        *fixture_name: Components of the CSV fixture file path.
        encoding: Text encoding to use when reading the file (default: "utf-8").

    Returns:
        Generator[list[str], None, None]: A generator of lists, one for each row in the CSV file.

    Raises:
        FileNotFoundError: If the fixture file doesn't exist.
        csv.Error: If the file contains malformed CSV data.

    Example:
        Reading CSV data with headers:
        
        ```python
        def test_user_data(read_csv_fixture):
            rows = read_csv_fixture("data", "users.csv")
            header = next(rows)  # First row is typically headers
            assert header == ["name", "age", "email"]
        ```
        
        Processing sales data from a CSV file:
        
        ```python
        def test_sales_data(read_csv_fixture):
            sales = read_csv_fixture("reports", "sales.csv")
            total_rows = sum(1 for row in sales)
            assert total_rows > 0
        ```

    """

    def _read_csv_fixture(
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
    ) -> Generator[list[str], None, None]:
        path = path_for_fixture(*fixture_name)
        with open(path, encoding=encoding) as f:
            yield from csv.reader(f)

    return _read_csv_fixture


@pytest.fixture
def read_csv_dict_fixture(path_for_fixture):
    """
    Read and parse a CSV fixture file as dictionaries.

    This fixture returns a function that reads CSV fixture files using
    Python's built-in csv.DictReader. The result is a generator of dictionaries,
    one for each row in the file, allowing for memory-efficient processing
    of large CSV files. Each row is returned as a dictionary with column
    headers as keys and row values as string values.

    Args:
        path_for_fixture: Function to get paths to fixture files.

    Returns:
        Callable: A function that reads and parses CSV fixture files as dictionaries.

    The returned function accepts:
        *fixture_name: Components of the CSV fixture file path.
        encoding: Text encoding to use when reading the file (default: "utf-8").

    Returns:
        Generator[dict[str, str], None, None]: A generator of dictionaries, one for each row in the CSV file.

    Raises:
        FileNotFoundError: If the fixture file doesn't exist.
        csv.Error: If the file contains malformed CSV data.

    Example:
        Reading user data as dictionaries:
        
        ```python
        def test_user_data(read_csv_dict_fixture):
            users = read_csv_dict_fixture("data", "users.csv")
            first_user = next(users)
            assert first_user["name"] == "Alice"
            assert first_user["age"] == "30"
        ```
        
        Processing sales records with dict access:
        
        ```python
        def test_sales_records(read_csv_dict_fixture):
            sales = read_csv_dict_fixture("reports", "sales.csv")
            for record in sales:
                assert "product" in record
                assert "revenue" in record
        ```

    """

    def _read_csv_dict_fixture(
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
    ) -> Generator[dict[str, str], None, None]:
        path = path_for_fixture(*fixture_name)
        with open(path, encoding=encoding) as f:
            yield from csv.DictReader(f)

    return _read_csv_dict_fixture


@pytest.fixture
def read_yaml_fixture(path_for_fixture):
    """
    Read and parse a YAML fixture file.

    This fixture returns a function that reads YAML fixture files and
    automatically parses them into Python objects (typically dictionaries).
    Requires the PyYAML library to be installed.

    Args:
        path_for_fixture: Function to get paths to fixture files.

    Returns:
        Callable: A function that reads and parses YAML fixture files.

    The returned function accepts:
        *fixture_name: Components of the YAML fixture file path.
        encoding: Text encoding to use when reading the file (default: "utf-8").
        unsafe_load: If True, uses yaml.FullLoader instead of yaml.SafeLoader (default: False).
                    WARNING: Only use unsafe_load=True with trusted YAML content.

    Returns:
        Any: The parsed YAML data (typically a dictionary or list).

    Raises:
        ImportError: If PyYAML is not installed.
        FileNotFoundError: If the fixture file doesn't exist.
        yaml.YAMLError: If the file contains invalid YAML syntax.

    Example:
        Reading configuration from a YAML file:
        
        ```python
        def test_config_data(read_yaml_fixture):
            config = read_yaml_fixture("config", "settings.yaml")
            assert config["database"]["host"] == "localhost"
            assert config["debug"] is False
        ```
        
        Processing user data from a YAML file:
        
        ```python
        def test_user_list(read_yaml_fixture):
            users = read_yaml_fixture("data", "users.yaml")
            assert len(users) > 0
            assert users[0]["name"] == "Alice"
        ```

    Note:
        By default, uses yaml.SafeLoader for security. Only use unsafe_load=True
        if you trust the YAML content and need features not supported by SafeLoader.

    """

    def _read_yaml_fixture(
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
        unsafe_load: bool = False,
    ) -> Any:
        if yaml is None:
            raise ImportError(
                "PyYAML is required to use read_yaml_fixture. Install it: https://pypi.org/project/PyYAML/"
            )

        path = path_for_fixture(*fixture_name)
        with open(path, encoding=encoding) as f:
            loader = yaml.FullLoader if unsafe_load else yaml.SafeLoader
            return yaml.load(f, Loader=loader)

    return _read_yaml_fixture
