"""Module containing pytest fixtures."""

import json
import os
from collections.abc import Callable
from pathlib import Path

import pytest


def pytest_configure(config):
    """Configure pytest plugin."""


@pytest.fixture
def fixtures_path(pytestconfig):
    """
    Get the path to the test fixtures directory.

    This fixture provides a Path object pointing to the standard location
    for test fixtures: `tests/fixtures/` relative to the project root.

    Override this fixture if you want to use a different path for your fixtures.


    Args:
        pytestconfig: The pytest configuration object.

    Returns:
        Path: A pathlib.Path object pointing to the fixtures directory.

    Example:
        >>> def test_something(fixtures_path):
        ...     assert fixtures_path.exists()
        ...     assert fixtures_path.name == "fixtures"

    """
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
        >>> def test_data_file(path_for_fixture):
        ...     data_path = path_for_fixture("data", "sample.json")
        ...     assert data_path.suffix == ".json"
        ...
        >>> def test_optional_fixture(path_for_fixture):
        ...     # Won't raise error if file doesn't exist
        ...     path = path_for_fixture("optional", "file.txt", must_exist=False)

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
        >>> def test_text_fixture(read_fixture):
        ...     content = read_fixture("data", "sample.txt")
        ...     assert "hello" in content
        ...
        >>> def test_binary_fixture(read_fixture):
        ...     data = read_fixture("data", "image.png", mode="rb", deserialize=lambda x: x)
        ...     assert data.startswith(b'\x89PNG')

    """

    def _read_fixture(
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
        mode: str = "r",
        deserialize: Callable = lambda x: x,
    ) -> str:
        path = path_for_fixture(*fixture_name)
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
        >>> def test_config_data(read_json_fixture):
        ...     config = read_json_fixture("config", "settings.json")
        ...     assert config["database"]["host"] == "localhost"
        ...
        >>> def test_user_data(read_json_fixture):
        ...     users = read_json_fixture("data", "users.json")
        ...     assert len(users["users"]) > 0

    """

    def _read_json_fixture(
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
    ) -> dict:
        return read_fixture(*fixture_name, encoding=encoding, deserialize=json.loads)

    return _read_json_fixture


@pytest.fixture
def read_jsonl_fixture(read_fixture):
    """
    Read and parse a JSONL (JSON Lines) fixture file.

    This fixture returns a function that reads JSONL fixture files, where
    each line contains a separate JSON object. The result is a list of
    dictionaries, one for each line in the file.

    Args:
        read_fixture: The base fixture reading function.

    Returns:
        Callable: A function that reads and parses JSONL fixture files.

    The returned function accepts:
        *fixture_name: Components of the JSONL fixture file path.
        must_exist: If True, raises FileNotFoundError if the fixture doesn't exist.
        encoding: Text encoding to use when reading the file (default: "utf-8").

    Returns:
        list[dict]: A list of dictionaries, one for each JSON object in the file.

    Raises:
        FileNotFoundError: If must_exist=True and the fixture file doesn't exist.
        json.JSONDecodeError: If any line contains invalid JSON.

    Example:
        >>> def test_log_entries(read_jsonl_fixture):
        ...     logs = read_jsonl_fixture("logs", "access.jsonl")
        ...     assert len(logs) > 0
        ...     assert "timestamp" in logs[0]
        ...
        >>> def test_user_records(read_jsonl_fixture):
        ...     users = read_jsonl_fixture("data", "users.jsonl")
        ...     assert all("id" in user for user in users)

    """

    def _read_jsonl_fixture(
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
    ) -> list[dict]:
        def deserialize(x: str) -> list[dict]:
            return [json.loads(line) for line in x.splitlines()]

        return read_fixture(*fixture_name, encoding=encoding, deserialize=deserialize)

    return _read_jsonl_fixture
