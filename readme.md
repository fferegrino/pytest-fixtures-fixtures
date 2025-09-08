# pytest fixtures fixtures

Fixtures, for fixtures. Handy fixtures to access your test fixtures from your _pytest_ tests.

## Installation

```bash
pip install pytest-fixtures-fixtures
```

## Fixture Usage Guide

This plugin provides several fixtures to help you read and interact with test fixture files in your pytest tests.

Everything starts whith where you define your fixtures, by default, this plugin expects your fixtures to live in a folder named `tests/fixtures` from the root of your project. For example:

```text
src
├── script.py
tests/
├── fixtures/
│   ├── users_data.txt
│   ├── app_config.json
│   └── error_logs.jsonl
└── test_script.py
```

If you wanted to read the `users_data.txt` file, you would use the `read_fixture` fixture:

```python
def test_users_data(read_fixture):
    data = read_fixture("users_data.txt")
    assert "Alice" in data
```

If you wanted to read the `app_config.json` file, you would use the `read_json_fixture` fixture:

```python
def test_app_config(read_json_fixture):
    config = read_json_fixture("app_config.json")
    assert config["database"]["host"] == "localhost"
    assert config["debug"] is True
```

There are more fixtures available to read different types of fixture files, including providing your own deserialization function. You can read the [Fixtures Usage](docs/fixtures-usage.md) docs for more information.

## Configure default fixtures directory

You can configure the default fixtures directory in several ways, the most common one is by redefining the `fixtures_path` fixture in your tests:

```python
@pytest.fixture
def fixtures_path(tmp_path):
    """Use a temporary directory for fixtures."""
    path = tmp_path / "my_fixtures"
    path.mkdir()
    return path
```

You can read more about how to configure the default fixtures directory using configuration files or CLI in the [Configuration](docs/configuration.md) docs.

## Use fixtures to parametrize your tests

This plugin also provides a decorator to parametrize your tests using fixture files, for example:

```csv
id,a,b,c
add_positive,1,2,3
add_negative,1,-1,0
add_zero,5,0,5
```

```python
@parametrize_from_fixture("data.csv")
def test_addition(a, b, c):
    assert int(a) + int(b) == int(c)
```

Will be expanded into three tests, each with different values for `a`, `b`, and `c` based on the data in the fixture file.

You can read more about how to use the `parametrize_from_fixture` decorator in the [Parametrize](docs/parametrize.md) docs.

## A good example

`pytest-fixtures-fixtures` is tested using itself, you can see the tests in the [tests](tests) directory.

## Documentation

- **[Fixtures Usage](docs/fixtures-usage.md)** - Complete guide to all available fixtures
- **[Test Parametrization](docs/parametrize.md)** - Data-driven testing with external files
- **[Configuration](docs/configuration.md)** - Customize fixtures directory and behavior

## Why Use This Plugin?

 - **Clean separation** of test data and test logic  
 - **Multiple formats** supported with consistent API  
 - **Automatic validation** and clear error messages  
 - **Flexible configuration** for different environments  
 - **Parametrization support** with custom test IDs  

## Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
