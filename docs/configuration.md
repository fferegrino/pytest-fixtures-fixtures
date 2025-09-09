# Configuration Guide

This guide covers how to configure the fixtures directory and customize the plugin behavior.

There are two main things you can configure, and it is important to know the difference between them.

- **Custom Fixture Directory**: This is the directory where the fixtures are stored.
- **Parametrization**: This is the way to parametrize the tests using the fixtures.

Sadly, due to the way `pytest` works, they are independent of each other.

## Runtime fixture directory

**When your tests are running**, the fixture directory is set to the `tests/fixtures/` directory by default, you can override the path in several ways.

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

Here are some practical examples when you would want to override the fixture directory.

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

## Configuration for Parametrization

The `parametrize_from_fixture` decorator does not work at test runtime as tests need to be discovered before they are run, so you have several options to configure the fixtures directory for parametrization.

### Option 1: Environment Variable (Recommended)

Set the `PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE` environment variable to specify the fixtures directory for parametrization:

```bash
# Set environment variable for current session
export PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE="tests/custom_fixtures"

# Run tests - all parametrized tests will use the custom path
pytest

# Or set it for a single command
PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE="tests/integration_fixtures" pytest
```

You can also set this in your CI/CD configuration or development environment setup:

```bash
# In .env file or CI configuration
PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE=/path/to/shared/fixtures
```

### Option 2: Explicit fixtures_dir Parameter

Override the fixtures directory for specific tests by passing the `fixtures_dir` argument to the decorator:

```python
from pytest_fixtures_fixtures import parametrize_from_fixture

# Uses the default or environment-configured fixtures directory
@parametrize_from_fixture("test_data.csv")
def test_with_configured_path(a, b, c):
    assert int(a) + int(b) == int(c)

# Override for specific test
@parametrize_from_fixture("test_data.csv", fixtures_dir="custom/path")
def test_with_custom_path(a, b, c):
    assert int(a) + int(b) == int(c)
```

### Configuration Precedence

The fixtures directory is determined in the following order of precedence:

1. **Explicit `fixtures_dir` parameter** (highest priority)
2. **`PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE` environment variable**
3. **Default path** (`tests/fixtures/` relative to current working directory)

### Practical Examples

**Example 1: Different fixtures for different test environments**

```bash
# Development fixtures
export PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE="tests/fixtures/dev"
pytest

# Production-like fixtures
export PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE="tests/fixtures/prod"
pytest

# Integration test fixtures
export PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE="tests/fixtures/integration"
pytest tests/integration/
```

**Example 2: Mixed configuration**

```python
# Most tests use environment-configured path
@parametrize_from_fixture("common_data.csv")
def test_common_functionality(value, expected):
    assert process(value) == expected

# Special test uses custom fixtures
@parametrize_from_fixture("edge_cases.json", fixtures_dir="tests/special_fixtures")
def test_edge_cases(input_data, expected_output):
    assert handle_edge_case(input_data) == expected_output
```

**Example 3: CI/CD Configuration**

```yaml
# GitHub Actions example
- name: Run unit tests
  env:
    PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE: tests/fixtures/unit
  run: pytest tests/unit/

- name: Run integration tests  
  env:
    PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE: tests/fixtures/integration
  run: pytest tests/integration/
```
