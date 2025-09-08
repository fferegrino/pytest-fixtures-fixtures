# Configuration Guide

This guide covers how to configure the fixtures directory and customize the plugin behavior.

## Custom Fixture Directory

You can override the default fixtures directory (`tests/fixtures/`) in several ways:

### Using Command Line Option

Use the `--fixtures-fixtures-path` option to specify a custom fixtures directory:

```bash
# Run tests with a custom fixtures directory
pytest --fixtures-fixtures-path=my_custom_fixtures

# Use relative path from project root
pytest --fixtures-fixtures-path=tests/my_fixtures

# Use absolute path
pytest --fixtures-fixtures-path=/path/to/my/fixtures
```

### Using Configuration Files

**In `pytest.ini`:**

```ini
[pytest]
addopts = --fixtures-fixtures-path=tests/custom_fixtures
```

**In `pyproject.toml`:**

```toml
[tool.pytest.ini_options]
addopts = "--fixtures-fixtures-path=tests/custom_fixtures"
```

### Programmatically Override the Fixture

Override the default fixtures path for specific tests by redefining the fixture:

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

## Practical Configuration Examples

### Example 1: Different fixtures for different environments

```bash
# Development fixtures
pytest --fixtures-fixtures-path=tests/fixtures/dev

# Production-like fixtures  
pytest --fixtures-fixtures-path=tests/fixtures/prod

# Integration test fixtures
pytest --fixtures-fixtures-path=tests/fixtures/integration
```

### Example 2: Shared fixtures across projects

```bash
# Use fixtures from a shared location
pytest --fixtures-fixtures-path=/shared/test-fixtures/common
```

### Example 3: Configuration per test suite

```toml
# pyproject.toml
[tool.pytest.ini_options]
# Default fixtures for unit tests
addopts = "--fixtures-fixtures-path=tests/fixtures/unit"
```

Then override for integration tests:

```bash
pytest tests/integration/ --fixtures-fixtures-path=tests/fixtures/integration
```

## Environment-Specific Configuration

### Development vs Production Fixtures

You can maintain separate fixture sets for different environments:

```
tests/
├── fixtures/
│   ├── dev/
│   │   ├── database.json    # Small test database
│   │   └── config.yaml      # Development settings
│   ├── staging/
│   │   ├── database.json    # Staging-like data
│   │   └── config.yaml      # Staging settings
│   └── prod/
│       ├── database.json    # Production-like data
│       └── config.yaml      # Production settings
```

Then use:

```bash
# Run tests against development fixtures
pytest --fixtures-fixtures-path=tests/fixtures/dev

# Run tests against production-like fixtures
pytest --fixtures-fixtures-path=tests/fixtures/prod
```

### CI/CD Integration

In your CI/CD pipeline, you can use different fixture sets:

```yaml
# GitHub Actions example
- name: Run unit tests
  run: pytest tests/unit/ --fixtures-fixtures-path=tests/fixtures/unit

- name: Run integration tests  
  run: pytest tests/integration/ --fixtures-fixtures-path=tests/fixtures/integration
```

## Fixture Organization Best Practices

### Recommended Directory Structure

```
tests/
├── fixtures/
│   ├── api/
│   │   ├── responses/
│   │   │   ├── users.json
│   │   │   └── products.json
│   │   └── requests/
│   │       ├── create_user.json
│   │       └── update_product.json
│   ├── data/
│   │   ├── users.csv
│   │   ├── products.yaml
│   │   └── orders.jsonl
│   ├── config/
│   │   ├── settings.yaml
│   │   └── database.json
│   └── logs/
│       ├── error.jsonl
│       └── access.jsonl
└── test_*.py
```

### Naming Conventions

- Use descriptive names that indicate the fixture's purpose
- Group related fixtures in subdirectories
- Use consistent file extensions (`.json`, `.yaml`, `.csv`, etc.)
- Include version numbers for evolving fixtures (`users_v1.json`, `users_v2.json`)

### Size and Performance Considerations

- Keep fixture files reasonably sized (< 1MB for fast test loading)
- Use compressed formats (`.jsonl`) for large datasets
- Consider splitting large fixtures into smaller, focused files
- Use symbolic links for shared fixtures between test suites

## Configuration for Parametrization

The `parametrize_from_fixture` decorator respects the same fixtures directory configuration:

```python
from pytest_fixtures_fixtures import parametrize_from_fixture

# Uses the configured fixtures directory
@parametrize_from_fixture("test_data.csv")
def test_with_configured_path(a, b, c):
    assert int(a) + int(b) == int(c)

# Override for specific test
@parametrize_from_fixture("test_data.csv", fixtures_dir="custom/path")
def test_with_custom_path(a, b, c):
    assert int(a) + int(b) == int(c)
```
