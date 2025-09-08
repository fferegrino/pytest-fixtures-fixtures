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

    actual = list(read_jsonl_fixture("test.jsonl"))
    assert actual == jsonl


def test_read_jsonl_fixture_encoding(read_jsonl_fixture, temp_dir):
    """Test read_jsonl_fixture with different encoding."""
    data = [{"message": "Hello 世界"}, {"emoji": "🌍"}]
    test_file = temp_dir / "unicode.jsonl"
    with open(test_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    result = list(read_jsonl_fixture("unicode.jsonl", encoding="utf-8"))
    assert result == data


def test_read_jsonl_fixture_invalid_json_line(read_jsonl_fixture, temp_dir):
    """Test read_jsonl_fixture with invalid JSON line raises error."""
    test_file = temp_dir / "invalid.jsonl"
    with open(test_file, "w") as f:
        f.write('{"valid": "json"}\n')
        f.write("{ invalid json }\n")
        f.write('{"another": "valid"}\n')

    with pytest.raises(json.JSONDecodeError):
        list(read_jsonl_fixture("invalid.jsonl"))


def test_read_jsonl_fixture_empty_file(read_jsonl_fixture, temp_dir):
    """Test read_jsonl_fixture with empty file returns empty list."""
    test_file = temp_dir / "empty.jsonl"
    test_file.write_text("")

    result = list(read_jsonl_fixture("empty.jsonl"))
    assert result == []


def test_read_jsonl_fixture_single_line(read_jsonl_fixture, temp_dir):
    """Test read_jsonl_fixture with single JSON line."""
    data = [{"id": 1, "name": "Alice"}]
    test_file = temp_dir / "single.jsonl"
    with open(test_file, "w") as f:
        f.write(json.dumps(data[0]) + "\n")

    result = list(read_jsonl_fixture("single.jsonl"))
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

    result = list(read_jsonl_fixture("mixed.jsonl"))
    assert result == data
    assert len(result) == 3
    assert result[0]["type"] == "user"
    assert result[1]["type"] == "event"
    assert result[2]["type"] == "config"


def test_read_jsonl_fixture_nonexistent_file(read_jsonl_fixture):
    """Test read_jsonl_fixture with nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        list(read_jsonl_fixture("nonexistent.jsonl"))


def test_read_csv_fixture(read_csv_fixture, temp_dir):
    """Test read_csv_fixture with valid CSV file."""
    temp_dir_file = temp_dir / "test.csv"
    expected = [["name", "age"], ["Alice", "30"], ["Bob", "25"]]
    csv_data = ["name,age", "Alice,30", "Bob,25"]
    temp_dir_file.write_text("\n".join(csv_data))

    actual = list(read_csv_fixture("test.csv"))
    assert actual == expected


def test_read_csv_dict_fixture(read_csv_dict_fixture, temp_dir):
    """Test read_csv_dict_fixture with valid CSV file."""
    temp_dir_file = temp_dir / "test.csv"
    csv_data = ["name,age,city", "Alice,30,New York", "Bob,25,London"]
    temp_dir_file.write_text("\n".join(csv_data))

    actual = list(read_csv_dict_fixture("test.csv"))
    expected = [{"name": "Alice", "age": "30", "city": "New York"}, {"name": "Bob", "age": "25", "city": "London"}]
    assert actual == expected


def test_read_csv_dict_fixture_encoding(read_csv_dict_fixture, temp_dir):
    """Test read_csv_dict_fixture with different encoding."""
    data = ["name,location", "José,São Paulo", "François,Café de Paris"]
    test_file = temp_dir / "unicode.csv"
    test_file.write_text("\n".join(data), encoding="utf-8")

    result = list(read_csv_dict_fixture("unicode.csv", encoding="utf-8"))
    expected = [{"name": "José", "location": "São Paulo"}, {"name": "François", "location": "Café de Paris"}]
    assert result == expected


def test_read_csv_dict_fixture_empty_file(read_csv_dict_fixture, temp_dir):
    """Test read_csv_dict_fixture with empty file returns empty list."""
    test_file = temp_dir / "empty.csv"
    test_file.write_text("")

    result = list(read_csv_dict_fixture("empty.csv"))
    assert result == []


def test_read_csv_dict_fixture_headers_only(read_csv_dict_fixture, temp_dir):
    """Test read_csv_dict_fixture with headers only."""
    test_file = temp_dir / "headers_only.csv"
    test_file.write_text("name,age,email")

    result = list(read_csv_dict_fixture("headers_only.csv"))
    assert result == []


def test_read_csv_dict_fixture_single_row(read_csv_dict_fixture, temp_dir):
    """Test read_csv_dict_fixture with single data row."""
    data = ["id,name,active", "1,Alice,true"]
    test_file = temp_dir / "single.csv"
    test_file.write_text("\n".join(data))

    result = list(read_csv_dict_fixture("single.csv"))
    expected = [{"id": "1", "name": "Alice", "active": "true"}]
    assert result == expected


def test_read_csv_dict_fixture_quoted_fields(read_csv_dict_fixture, temp_dir):
    """Test read_csv_dict_fixture with quoted CSV fields."""
    data = ["name,description", '"Alice Smith","A person who likes, commas"', '"Bob Jones","Simple description"']
    test_file = temp_dir / "quoted.csv"
    test_file.write_text("\n".join(data))

    result = list(read_csv_dict_fixture("quoted.csv"))
    expected = [
        {"name": "Alice Smith", "description": "A person who likes, commas"},
        {"name": "Bob Jones", "description": "Simple description"},
    ]
    assert result == expected


def test_read_csv_dict_fixture_nonexistent_file(read_csv_dict_fixture):
    """Test read_csv_dict_fixture with nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        list(read_csv_dict_fixture("nonexistent.csv"))


def test_read_yaml_fixture(read_yaml_fixture, temp_dir):
    """Test read_yaml_fixture with valid YAML file."""
    temp_dir_file = temp_dir / "test.yaml"
    data = {"name": "Alice", "age": 30, "active": True, "tags": ["user", "admin"]}
    yaml_content = yaml.dump(data)
    temp_dir_file.write_text(yaml_content)

    actual = read_yaml_fixture("test.yaml")
    assert actual == data


def test_read_yaml_fixture_encoding(read_yaml_fixture, temp_dir):
    """Test read_yaml_fixture with different encoding."""
    data = {"message": "Hello 世界", "location": "São Paulo", "café": "François"}
    test_file = temp_dir / "unicode.yaml"
    yaml_content = yaml.dump(data, allow_unicode=True)
    test_file.write_text(yaml_content, encoding="utf-8")

    result = read_yaml_fixture("unicode.yaml", encoding="utf-8")
    assert result == data


def test_read_yaml_fixture_list(read_yaml_fixture, temp_dir):
    """Test read_yaml_fixture with YAML list."""
    data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    test_file = temp_dir / "list.yaml"
    yaml_content = yaml.dump(data)
    test_file.write_text(yaml_content)

    result = read_yaml_fixture("list.yaml")
    assert result == data


def test_read_yaml_fixture_nested_structure(read_yaml_fixture, temp_dir):
    """Test read_yaml_fixture with complex nested YAML structure."""
    data = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {"username": "admin", "password": "secret"},
        },
        "features": {"debug": True, "cache": False},
        "servers": ["web1", "web2", "db1"],
    }
    test_file = temp_dir / "config.yaml"
    yaml_content = yaml.dump(data)
    test_file.write_text(yaml_content)

    result = read_yaml_fixture("config.yaml")
    assert result == data
    assert result["database"]["port"] == 5432
    assert len(result["servers"]) == 3


def test_read_yaml_fixture_safe_vs_unsafe_load(read_yaml_fixture, temp_dir):
    """Test read_yaml_fixture with safe vs unsafe loading."""
    # Simple data that works with both loaders
    data = {"simple": "value", "number": 42}
    test_file = temp_dir / "simple.yaml"
    yaml_content = yaml.dump(data)
    test_file.write_text(yaml_content)

    # Test safe loading (default)
    result_safe = read_yaml_fixture("simple.yaml", unsafe_load=False)
    assert result_safe == data

    # Test unsafe loading
    result_unsafe = read_yaml_fixture("simple.yaml", unsafe_load=True)
    assert result_unsafe == data


def test_read_yaml_fixture_invalid_yaml(read_yaml_fixture, temp_dir):
    """Test read_yaml_fixture with invalid YAML raises error."""
    test_file = temp_dir / "invalid.yaml"
    test_file.write_text("{ invalid: yaml: content }")

    with pytest.raises(yaml.YAMLError):
        read_yaml_fixture("invalid.yaml")


def test_read_yaml_fixture_empty_file(read_yaml_fixture, temp_dir):
    """Test read_yaml_fixture with empty file returns None."""
    test_file = temp_dir / "empty.yaml"
    test_file.write_text("")

    result = read_yaml_fixture("empty.yaml")
    assert result is None


def test_read_yaml_fixture_nonexistent_file(read_yaml_fixture):
    """Test read_yaml_fixture with nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        read_yaml_fixture("nonexistent.yaml")


def test_read_yaml_fixture_missing_pyyaml(path_for_fixture, temp_dir, monkeypatch):
    """Test read_yaml_fixture raises ImportError when PyYAML is not available."""
    # Mock yaml as None to simulate missing PyYAML
    import pytest_fixtures_fixtures.pytest_plugin as plugin_module

    monkeypatch.setattr(plugin_module, "yaml", None)

    # Re-create the fixture function with mocked yaml
    from pytest_fixtures_fixtures.pytest_plugin import read_yaml_fixture

    yaml_fixture_func = read_yaml_fixture.__wrapped__(path_for_fixture)

    with pytest.raises(ImportError, match="PyYAML is required to use read_yaml_fixture"):
        yaml_fixture_func("test.yaml")


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
