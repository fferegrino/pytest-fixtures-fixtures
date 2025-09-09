"""
Protocols for pytest fixtures.

This module defines the type protocols that describe the interfaces for
various fixture functions. These protocols can be used as type hints
in test functions to provide better type checking and IDE support.
"""

import os
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any, Protocol


class FixturePath(Protocol):
    """A callable that constructs paths inside the fixtures directory."""

    def __call__(self, *fixture_name: str | os.PathLike[str], must_exist: bool = True) -> Path:
        """
        Construct a path to a fixture file.

        This method creates a path to a fixture file within the fixtures directory.
        It's used by the `path_for_fixture` fixture to provide a consistent interface
        for accessing test fixture files.

        Args:
            *fixture_name: One or more path components (e.g., "data", "sample.json").
                Can be strings or path-like objects.
            must_exist: If True (default), raise FileNotFoundError if the file does not exist.

        Returns:
            The constructed fixture path.

        Raises:
            FileNotFoundError: If must_exist=True and the fixture file doesn't exist.

        Example:
            Using the FixturePath protocol in a test:

            ```python
            def test_fixture_path(path_for_fixture: FixturePath):
                # Construct a path to a fixture file
                data_path = path_for_fixture("data", "sample.json")
                assert data_path.suffix == ".json"

                # Check if a file exists without raising an error
                optional_path = path_for_fixture("optional", "file.txt", must_exist=False)
            ```

        """
        ...


class ReadFixture(Protocol):
    """A callable that reads and optionally deserializes fixture files."""

    def __call__(
        self,
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
        mode: str = "r",
        deserialize: Callable[[str | bytes], Any] = lambda x: x,
    ) -> Any:
        r"""
        Read and optionally deserialize a fixture file.

        This method reads fixture files with customizable encoding, file mode,
        and deserialization. It's used by various read fixture functions to
        provide a consistent interface for accessing fixture file contents.

        Args:
            *fixture_name: Components of the fixture file path. Can be strings or path-like objects.
            encoding: Text encoding to use when reading the file (default: "utf-8").
            mode: File open mode (default: "r" for text mode).
            deserialize: Function to process the file contents. Takes str or bytes and returns Any (default: identity).

        Returns:
            The result of applying the deserialize function to the file contents.

        Raises:
            FileNotFoundError: If the fixture file doesn't exist.
            UnicodeDecodeError: If the file cannot be decoded with the specified encoding.
            OSError: If there's an error reading the file.

        Example:
            Using the ReadFixture protocol in a test:

            ```python
            def test_read_fixture(read_fixture: ReadFixture):
                # Read a text file
                content = read_fixture("data", "sample.txt")
                assert "hello" in content

                # Read a binary file
                data = read_fixture("images", "logo.png", mode="rb", deserialize=lambda x: x)
                assert data.startswith(b'\x89PNG')
            ```

        """
        ...


class ReadJsonFixture(Protocol):
    """A callable that reads and parses JSON fixture files."""

    def __call__(
        self,
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
    ) -> dict:
        """
        Read and parse a JSON fixture file.

        This method reads JSON fixture files and automatically parses them
        into Python dictionaries.

        Args:
            *fixture_name: Components of the JSON fixture file path. Can be strings or path-like objects.
            encoding: Text encoding to use when reading the file (default: "utf-8").

        Returns:
            The parsed JSON data as a Python dictionary.

        Raises:
            FileNotFoundError: If the fixture file doesn't exist.
            json.JSONDecodeError: If the file contains invalid JSON.

        Example:
            Using the ReadJsonFixture protocol in a test:

            ```python
            def test_config_data(read_json_fixture: ReadJsonFixture):
                config = read_json_fixture("config", "settings.json")
                assert config["database"]["host"] == "localhost"
            ```

        """
        ...


class ReadJsonlFixture(Protocol):
    """A callable that reads and parses JSONL (JSON Lines) fixture files."""

    def __call__(
        self,
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
    ) -> Generator[dict, None, None]:
        """
        Read and parse a JSONL (JSON Lines) fixture file.

        This method reads JSONL fixture files, where each line contains a separate
        JSON object. The result is a generator of dictionaries, one for each line
        in the file.

        Args:
            *fixture_name: Components of the JSONL fixture file path. Can be strings or path-like objects.
            encoding: Text encoding to use when reading the file (default: "utf-8").

        Returns:
            A generator of dictionaries, one for each JSON object in the file.

        Raises:
            FileNotFoundError: If the fixture file doesn't exist.
            json.JSONDecodeError: If any line contains invalid JSON.

        Example:
            Using the ReadJsonlFixture protocol in a test:

            ```python
            def test_log_entries(read_jsonl_fixture: ReadJsonlFixture):
                logs = read_jsonl_fixture("logs", "access.jsonl")
                first_log = next(logs)
                assert "timestamp" in first_log
            ```

        """
        ...


class ReadCsvFixture(Protocol):
    """A callable that reads and parses CSV fixture files."""

    def __call__(
        self,
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
    ) -> Generator[list[str], None, None]:
        """
        Read and parse a CSV fixture file.

        This method reads CSV fixture files using Python's built-in csv.reader.
        The result is a generator of lists, one for each row in the file.
        Each row is returned as a list of strings.

        Args:
            *fixture_name: Components of the CSV fixture file path. Can be strings or path-like objects.
            encoding: Text encoding to use when reading the file (default: "utf-8").

        Returns:
            A generator of lists, one for each row in the CSV file.

        Raises:
            FileNotFoundError: If the fixture file doesn't exist.
            csv.Error: If the file contains malformed CSV data.

        Example:
            Using the ReadCsvFixture protocol in a test:

            ```python
            def test_user_data(read_csv_fixture: ReadCsvFixture):
                rows = read_csv_fixture("data", "users.csv")
                header = next(rows)  # First row is typically headers
                assert header == ["name", "age", "email"]
            ```

        """
        ...


class ReadCsvDictFixture(Protocol):
    """A callable that reads and parses CSV fixture files as dictionaries."""

    def __call__(
        self,
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
    ) -> Generator[dict[str, str], None, None]:
        """
        Read and parse a CSV fixture file as dictionaries.

        This method reads CSV fixture files using Python's built-in csv.DictReader.
        The result is a generator of dictionaries, one for each row in the file.
        Each row is returned as a dictionary with column headers as keys and
        row values as string values.

        Args:
            *fixture_name: Components of the CSV fixture file path. Can be strings or path-like objects.
            encoding: Text encoding to use when reading the file (default: "utf-8").

        Returns:
            A generator of dictionaries, one for each row in the CSV file.

        Raises:
            FileNotFoundError: If the fixture file doesn't exist.
            csv.Error: If the file contains malformed CSV data.

        Example:
            Using the ReadCsvDictFixture protocol in a test:

            ```python
            def test_user_data(read_csv_dict_fixture: ReadCsvDictFixture):
                users = read_csv_dict_fixture("data", "users.csv")
                first_user = next(users)
                assert first_user["name"] == "Alice"
            ```

        """
        ...


class ReadYamlFixture(Protocol):
    """A callable that reads and parses YAML fixture files."""

    def __call__(
        self,
        *fixture_name: str | os.PathLike[str],
        encoding: str = "utf-8",
        unsafe_load: bool = False,
    ) -> Any:
        """
        Read and parse a YAML fixture file.

        This method reads YAML fixture files and automatically parses them into
        Python objects (typically dictionaries). Requires the PyYAML library
        to be installed.

        Args:
            *fixture_name: Components of the YAML fixture file path. Can be strings or path-like objects.
            encoding: Text encoding to use when reading the file (default: "utf-8").
            unsafe_load: If True, uses yaml.FullLoader instead of yaml.SafeLoader (default: False).
                        WARNING: Only use unsafe_load=True with trusted YAML content.

        Returns:
            The parsed YAML data (typically a dictionary or list).

        Raises:
            ImportError: If PyYAML is not installed.
            FileNotFoundError: If the fixture file doesn't exist.
            yaml.YAMLError: If the file contains invalid YAML syntax.

        Example:
            Using the ReadYamlFixture protocol in a test:

            ```python
            def test_config_data(read_yaml_fixture: ReadYamlFixture):
                config = read_yaml_fixture("config", "settings.yaml")
                assert config["database"]["host"] == "localhost"
            ```

        """
        ...
