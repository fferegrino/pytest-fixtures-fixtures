# pytest fixtures fixtures

Handy fixtures to access your test fixtures from your _pytest_ tests.

## Installation

```bash
pip install pytest-fixtures-fixtures
```

## Usage

This plugin provides several fixtures to help you read and interact with test fixture files in your pytest tests.

### Basic Fixtures

#### `fixtures_path`

Get the path to your test fixtures directory **(defaults to `tests/fixtures/`).**

```python
def test_fixtures_directory(fixtures_path):
    assert fixtures_path.exists()
    assert fixtures_path.name == "fixtures"
    assert fixtures_path.parent.name == "tests"
```

#### `path_for_fixture`

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

### Reading Fixture Files

#### `read_fixture`

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

##### With custom deserialization

```python
import yaml # Depends on pyyaml

def test_read_yaml_file(read_fixture):

    def deserialize(x: str) -> dict:
        return yaml.safe_load(x)
    
    data = read_fixture("data", "config.yaml", deserialize=deserialize)
    assert data["database"]["host"] == "localhost"
    assert data["debug"] is True
```

#### `read_json_fixture`

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

#### `read_jsonl_fixture`

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

### Custom Fixture Directory

Override the default fixtures path for your tests:

```python
@pytest.fixture
def fixtures_path(tmp_path):
    """Use a temporary directory for fixtures."""
    path = tmp_path / "my_fixtures"
    path.mkdir()
    return path

def test_with_custom_path(read_fixture, fixtures_path):
    # Create a test file in the custom fixtures directory
    # Usually this is not recommended, but if you are using
    # a temporary directory for fixtures, this makes more sense.
    test_file = fixtures_path / "test.txt"
    test_file.write_text("custom content")
    
    # Read it using the fixture
    content = read_fixture("test.txt")
    assert content == "custom content"
```

### Error Handling

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

### Real-World Examples

Imagine you have a structure like this:

```text
tests/
├── fixtures/
│   ├── config/
│   │   └──  app.json
│   ├── data/
│   │   └── users.txt
│   ├── api/
│   │   └── user_response.json
│   └── logs/
│       └── errors.jsonl
└── test_*.py
```

You can use these fixtures to test your code:

#### Testing API Responses

```python
def test_api_response_parsing(read_json_fixture):
    """Test parsing of API response fixtures."""
    response = read_json_fixture("api", "user_response.json")
    
    assert response["status"] == "success"
    assert "data" in response
    assert response["data"]["id"] > 0
    assert response["data"]["email"].endswith("@example.com")
```

#### Testing Configuration Files

```python
def test_app_config(read_json_fixture):
    """Test application configuration loading."""
    config = read_json_fixture("config", "app.json")
    
    assert config["database"]["type"] == "postgresql"
    assert config["redis"]["host"] == "localhost"
    assert config["features"]["new_ui"] is True
```

#### Testing Log Analysis

```python
def test_error_log_analysis(read_jsonl_fixture):
    """Analyze error logs from JSONL fixtures."""
    errors = read_jsonl_fixture("logs", "errors.jsonl")
    
    # Filter for critical errors
    critical_errors = [e for e in errors if e.get("level") == "CRITICAL"]
    assert len(critical_errors) == 0, "No critical errors should be present"
    
    # Check error patterns
    error_types = [e.get("type") for e in errors]
    assert "database_connection" not in error_types
```

#### Testing Data Processing

```python
def test_data_validation(read_json_fixture):
    """Validate data structure from fixtures."""
    users = read_json_fixture("data", "users.json")
    
    # Validate required fields
    for user in users["users"]:
        assert "id" in user
        assert "email" in user
        assert "@" in user["email"]
        assert len(user["name"]) > 0
```
