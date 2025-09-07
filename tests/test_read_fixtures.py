import json

import pytest
import yaml


@pytest.fixture
def temp_dir(tmp_path):
    path = tmp_path / "fixtures"
    path.mkdir()
    return path


@pytest.fixture
def fixtures_path(temp_dir):
    return temp_dir


def test_read_json_fixture(read_json_fixture, temp_dir):
    """Test read_json_fixture with valid JSON file."""
    temp_dir_file = temp_dir / "test.json"
    dictionary = {"test": "test"}
    temp_dir_file.write_text(json.dumps(dictionary))

    actual = read_json_fixture("test.json")
    assert actual == dictionary


def test_read_json_fixture_encoding(read_json_fixture, temp_dir):
    """Test read_json_fixture with different encoding."""
    data = {"message": "Hello 世界", "emoji": "🌍"}
    test_file = temp_dir / "unicode.json"
    test_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    result = read_json_fixture("unicode.json", encoding="utf-8")
    assert result == data


def test_read_json_fixture_invalid_json(read_json_fixture, temp_dir):
    """Test read_json_fixture with invalid JSON raises error."""
    test_file = temp_dir / "invalid.json"
    test_file.write_text("{ invalid json }")

    with pytest.raises(json.JSONDecodeError):
        read_json_fixture("invalid.json")


def test_read_json_fixture_empty_file(read_json_fixture, temp_dir):
    """Test read_json_fixture with empty file."""
    test_file = temp_dir / "empty.json"
    test_file.write_text("")

    with pytest.raises(json.JSONDecodeError):
        read_json_fixture("empty.json")


def test_read_json_fixture_nested_structure(read_json_fixture, temp_dir):
    """Test read_json_fixture with complex nested JSON structure."""
    data = {
        "users": [
            {"id": 1, "name": "Alice", "settings": {"theme": "dark"}},
            {"id": 2, "name": "Bob", "settings": {"theme": "light"}},
        ],
        "metadata": {"version": "1.0", "created": "2024-01-01"},
    }
    test_file = temp_dir / "complex.json"
    test_file.write_text(json.dumps(data))

    result = read_json_fixture("complex.json")
    assert result == data
    assert len(result["users"]) == 2
    assert result["metadata"]["version"] == "1.0"


def test_read_json_fixture_nonexistent_file(read_json_fixture):
    """Test read_json_fixture with nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        read_json_fixture("nonexistent.json")


def test_read_jsonl_fixture(read_jsonl_fixture, temp_dir):
    """Test read_jsonl_fixture with valid JSONL file."""
    temp_dir_file = temp_dir / "test.jsonl"
    jsonl = [{"test": "test"}, {"test": "test2"}]
    with open(temp_dir_file, "w") as f:
        for item in jsonl:
            f.write(json.dumps(item) + "\n")

    actual = read_jsonl_fixture("test.jsonl")
    assert actual == jsonl


def test_read_jsonl_fixture_encoding(read_jsonl_fixture, temp_dir):
    """Test read_jsonl_fixture with different encoding."""
    data = [{"message": "Hello 世界"}, {"emoji": "🌍"}]
    test_file = temp_dir / "unicode.jsonl"
    with open(test_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    result = read_jsonl_fixture("unicode.jsonl", encoding="utf-8")
    assert result == data


def test_read_jsonl_fixture_invalid_json_line(read_jsonl_fixture, temp_dir):
    """Test read_jsonl_fixture with invalid JSON line raises error."""
    test_file = temp_dir / "invalid.jsonl"
    with open(test_file, "w") as f:
        f.write('{"valid": "json"}\n')
        f.write("{ invalid json }\n")
        f.write('{"another": "valid"}\n')

    with pytest.raises(json.JSONDecodeError):
        read_jsonl_fixture("invalid.jsonl")


def test_read_jsonl_fixture_empty_file(read_jsonl_fixture, temp_dir):
    """Test read_jsonl_fixture with empty file returns empty list."""
    test_file = temp_dir / "empty.jsonl"
    test_file.write_text("")

    result = read_jsonl_fixture("empty.jsonl")
    assert result == []


def test_read_jsonl_fixture_single_line(read_jsonl_fixture, temp_dir):
    """Test read_jsonl_fixture with single JSON line."""
    data = [{"id": 1, "name": "Alice"}]
    test_file = temp_dir / "single.jsonl"
    with open(test_file, "w") as f:
        f.write(json.dumps(data[0]) + "\n")

    result = read_jsonl_fixture("single.jsonl")
    assert result == data


def test_read_jsonl_fixture_mixed_types(read_jsonl_fixture, temp_dir):
    """Test read_jsonl_fixture with mixed JSON object types."""
    data = [
        {"type": "user", "id": 1, "name": "Alice"},
        {"type": "event", "action": "login", "timestamp": "2024-01-01T10:00:00Z"},
        {"type": "config", "settings": {"theme": "dark", "notifications": True}},
    ]
    test_file = temp_dir / "mixed.jsonl"
    with open(test_file, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    result = read_jsonl_fixture("mixed.jsonl")
    assert result == data
    assert len(result) == 3
    assert result[0]["type"] == "user"
    assert result[1]["type"] == "event"
    assert result[2]["type"] == "config"


def test_read_jsonl_fixture_nonexistent_file(read_jsonl_fixture):
    """Test read_jsonl_fixture with nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        read_jsonl_fixture("nonexistent.jsonl")


def test_read_fixture_with_custom_yaml_deserialize(read_fixture, temp_dir):
    """Test read_fixture with custom YAML deserialization."""
    temp_dir_file = temp_dir / "test.yaml"
    yaml_data = yaml.dump({"test": "test"})
    temp_dir_file.write_text(yaml_data)

    actual = read_fixture("test.yaml", deserialize=yaml.safe_load)
    assert actual == {"test": "test"}


def test_read_fixture_binary_mode(read_fixture, temp_dir):
    """Test read_fixture with binary mode."""
    binary_data = b"binary content with \x00 null bytes"
    test_file = temp_dir / "test.bin"
    test_file.write_bytes(binary_data)

    result = read_fixture("test.bin", mode="rb", deserialize=lambda x: x)
    assert result == binary_data
    assert isinstance(result, bytes)


@pytest.mark.parametrize("content, encoding", [("Hello 世界 🌍", "utf-8"), ("Hello café", "latin-1")])
def test_read_fixture_different_encoding(read_fixture, temp_dir, content, encoding):
    """Test read_fixture with different text encodings."""
    # Test with UTF-8 (default)
    test_file = temp_dir / f"{encoding}.txt"
    test_file.write_text(content, encoding=encoding)

    result = read_fixture(f"{encoding}.txt", encoding=encoding)
    assert result == content


def test_read_fixture_identity_deserialize(read_fixture, temp_dir):
    """Test read_fixture with default identity deserialization."""
    content = "plain text content"
    test_file = temp_dir / "plain.txt"
    test_file.write_text(content)

    # Test with default deserialize (identity function)
    result = read_fixture("plain.txt")
    assert result == content

    # Test with explicit identity function
    result = read_fixture("plain.txt", deserialize=lambda x: x)
    assert result == content


def test_read_fixture_custom_deserialize(read_fixture, temp_dir):
    """Test read_fixture with custom deserialization function."""
    content = "line1\nline2\nline3"
    test_file = temp_dir / "lines.txt"
    test_file.write_text(content)

    # Custom deserialization that splits into lines
    result = read_fixture("lines.txt", deserialize=lambda x: x.splitlines())
    assert result == ["line1", "line2", "line3"]


def test_read_fixture_nonexistent_file(read_fixture):
    """Test read_fixture with nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        read_fixture("nonexistent.txt")
