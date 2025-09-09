# Fixture Usage Guide

This guide covers all the available fixtures for reading and interacting with test fixture files.

## Overview

This plugin provides several fixtures to help you read and interact with test fixture files in your pytest tests. All fixtures work with the configurable `fixtures_path` which defaults to `tests/fixtures/` in your project.

## Basic Fixtures

### `fixtures_path`

Get the path to your test fixtures directory **(defaults to `tests/fixtures/`).**

```python
def test_fixtures_directory(fixtures_path):
    assert fixtures_path.exists()
    assert fixtures_path.name == "fixtures"
    assert fixtures_path.parent.name == "tests"
```

### `path_for_fixture`

Get a Path object for a specific fixture file.

```python
def test_get_fixture_path(path_for_fixture):
    # Get path to a fixture file
    config_path = path_for_fixture("config", "settings.json")
    assert config_path.suffix == ".json"
    
    # Allow non-existing files (useful for creating new fixtures)
    new_path = path_for_fixture("new", "file.txt", must_exist=False)
    assert not new_path.exists()
```

## Reading Fixture Files

### `read_fixture`

Read any type of fixture file with custom deserialization.

```python
def test_read_text_file(read_fixture):
    # Read plain text
    content = read_fixture("data", "sample.txt")
    assert "hello" in content

def test_read_binary_file(read_fixture):
    # Read binary files
    data = read_fixture("images", "logo.png", mode="rb", deserialize=lambda x: x)
    assert data.startswith(b'\x89PNG')

def test_read_with_custom_encoding(read_fixture):
    # Read with specific encoding
    content = read_fixture("data", "unicode.txt", encoding="utf-8")
    assert "世界" in content
```

#### With custom deserialization

```python
import yaml # Depends on pyyaml

def test_read_yaml_file(read_fixture):

    def deserialize(x: str) -> dict:
        return yaml.safe_load(x)
    
    data = read_fixture("data", "config.yaml", deserialize=deserialize)
    assert data["database"]["host"] == "localhost"
    assert data["debug"] is True
```

### `read_json_fixture`

Read and parse JSON fixture files.

```python
def test_read_json_config(read_json_fixture):
    config = read_json_fixture("config", "settings.json")
    assert config["database"]["host"] == "localhost"
    assert config["debug"] is True

def test_read_json_with_unicode(read_json_fixture):
    data = read_json_fixture("data", "unicode.json", encoding="utf-8")
    assert data["message"] == "Hello 世界"

def test_read_complex_json(read_json_fixture):
    users = read_json_fixture("data", "users.json")
    assert len(users["users"]) > 0
    assert all("id" in user for user in users["users"])
```

### `read_jsonl_fixture`

Read and parse JSONL (JSON Lines) fixture files.

```python
def test_read_jsonl_logs(read_jsonl_fixture):
    logs = read_jsonl_fixture("logs", "access.jsonl")
    assert len(logs) > 0
    assert "timestamp" in logs[0]
    assert "method" in logs[0]

def test_read_jsonl_users(read_jsonl_fixture):
    users = read_jsonl_fixture("data", "users.jsonl")
    assert all("id" in user for user in users)
    assert all("name" in user for user in users)

def test_read_mixed_jsonl(read_jsonl_fixture):
    events = read_jsonl_fixture("events", "mixed.jsonl")
    # Each line can be a different type of JSON object
    assert any(event.get("type") == "user" for event in events)
    assert any(event.get("type") == "system" for event in events)
```

### `read_csv_fixture` and `read_csv_dict_fixture`

Read and parse CSV fixture files.

```python
def test_read_csv_as_rows(read_csv_fixture):
    """Read CSV as rows (list of lists)."""
    rows = list(read_csv_fixture("data", "users.csv"))
    header = rows[0]  # First row is headers
    assert header == ["name", "age", "email"]
    
    first_user = rows[1]
    assert first_user[0] == "Alice"  # name
    assert first_user[1] == "30"     # age (as string)

def test_read_csv_as_dicts(read_csv_dict_fixture):
    """Read CSV as dictionaries."""
    users = list(read_csv_dict_fixture("data", "users.csv"))
    
    assert users[0]["name"] == "Alice"
    assert users[0]["age"] == "30"
    assert users[0]["email"] == "alice@example.com"
```

### `read_yaml_fixture`

Read and parse YAML fixture files (requires PyYAML).

```python
def test_read_yaml_config(read_yaml_fixture):
    """Read YAML configuration."""
    config = read_yaml_fixture("config", "settings.yaml")
    
    assert config["database"]["host"] == "localhost"
    assert config["features"]["debug"] is True
    assert len(config["servers"]) == 3

def test_read_yaml_list(read_yaml_fixture):
    """Read YAML list of items."""
    users = read_yaml_fixture("data", "users.yaml")
    
    assert len(users) == 2
    assert users[0]["name"] == "Alice"
    assert users[1]["name"] == "Bob"
```

## Using Type Protocols (Recommended)

For better type safety and IDE support, we recommend using the provided type protocols as type hints in your test functions. These protocols describe the exact interface of each fixture, providing better autocomplete, type checking, and documentation.

??? question "What are protocols?"

    Protocols are a way to define structural typing in Python. They describe the interface (method signatures) that a type should have, without requiring inheritance. When you use a protocol as a type hint, any object that implements the required interface will be accepted.

### Available Protocols

The plugin provides protocols for all fixture types:

- `FixturePath` - for the `path_for_fixture` fixture
- `ReadFixture` - for the `read_fixture` fixture  
- `ReadJsonFixture` - for the `read_json_fixture` fixture
- `ReadJsonlFixture` - for the `read_jsonl_fixture` fixture
- `ReadCsvFixture` - for the `read_csv_fixture` fixture
- `ReadCsvDictFixture` - for the `read_csv_dict_fixture` fixture
- `ReadYamlFixture` - for the `read_yaml_fixture` fixture

### How to Use Protocols

Import the protocols and use them as type hints in your test functions:

```python
from pytest_fixtures_fixtures import ReadJsonFixture

def test_with_type_hints(read_json_fixture: ReadJsonFixture):
    # Your IDE now provides better autocomplete and type checking!
    config = read_json_fixture("config", "settings.json")
    assert config["database"]["host"] == "localhost"
```

## Error Handling

The fixtures provide clear error messages for common issues:

```python
def test_file_not_found(read_json_fixture):
    with pytest.raises(FileNotFoundError):
        read_json_fixture("nonexistent.json")

def test_invalid_json(read_json_fixture, temp_dir):
    # Create invalid JSON file
    invalid_file = temp_dir / "invalid.json"
    invalid_file.write_text("{ invalid json }")
    
    with pytest.raises(json.JSONDecodeError):
        read_json_fixture("invalid.json")

def test_invalid_jsonl_line(read_jsonl_fixture, temp_dir):
    # Create JSONL with invalid line
    invalid_file = temp_dir / "invalid.jsonl"
    with open(invalid_file, "w") as f:
        f.write('{"valid": "json"}\n')
        f.write('{ invalid json }\n')
    
    with pytest.raises(json.JSONDecodeError):
        read_jsonl_fixture("invalid.jsonl")
```
