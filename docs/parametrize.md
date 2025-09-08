# Test Parametrization from Files

The `parametrize_from_fixture` decorator allows you to parametrize tests using data from external files. This is particularly useful for data-driven testing where you want to separate test logic from test data.

!!! warning

    This decorator expects the data files to be in the `tests/fixtures/` directory by default – this can not be changed for now.

## Quick Start

Given a CSV file with test data:

```csv
id,a,b,c
add_positive,1,2,3
add_negative,1,-1,0
add_zero,5,0,5
```

You can parametrize a test function like this:

```python
from pytest_fixtures_fixtures import parametrize_from_fixture

@parametrize_from_fixture("data.csv")
def test_addition(a, b, c):
    assert int(a) + int(b) == int(c)
```

This will expand into three separate tests:
- `test_addition[add_positive]`
- `test_addition[add_negative]`  
- `test_addition[add_zero]`

## Supported File Formats

### CSV Files

CSV files use the first row as headers to define parameter names.

```csv
id,username,password,expected_status
valid_login,alice,secret123,200
invalid_password,alice,wrong,401
missing_user,bob,anything,404
```

### JSON Files

JSON files should contain an array of objects:

```json
[
    {"id": "valid_request", "method": "GET", "endpoint": "/users", "status": 200},
    {"id": "invalid_endpoint", "method": "GET", "endpoint": "/invalid", "status": 404}
]
```

### YAML Files

YAML files should contain a list of dictionaries:

```yaml
- id: config_dev
  environment: development
  debug: true
  database: sqlite
- id: config_prod  
  environment: production
  debug: false
  database: postgresql
```

### JSONL Files

JSONL files contain one JSON object per line:

```jsonl
{"id": "user_admin", "role": "admin", "permissions": ["read", "write", "delete"]}
{"id": "user_guest", "role": "guest", "permissions": ["read"]}
```

## Custom Test IDs

The decorator automatically extracts test IDs from an `id` field in your data files. When present, these IDs are used to make test identification more meaningful.

### Without IDs (default pytest behavior)
```csv
a,b,c
1,2,3
3,4,7
```
Results in: `test_addition[1-2-3]`, `test_addition[3-4-7]`

### With IDs (custom meaningful names)
```csv
id,a,b,c
simple_addition,1,2,3
with_larger_numbers,3,4,7
```
Results in: `test_addition[simple_addition]`, `test_addition[with_larger_numbers]`

## Advanced Options

### Custom ID Field

You can specify a different field name for test IDs:

```python
@parametrize_from_fixture("test_data.csv", id_field="test_name")
def test_with_custom_id_field(param1, param2):
    # Uses 'test_name' column for test IDs
    pass
```

### Disable ID Extraction

Set `id_field=None` to disable automatic ID extraction:

```python
@parametrize_from_fixture("test_data.csv", id_field=None)
def test_with_default_ids(param1, param2):
    # Uses pytest's default ID generation
    pass
```

### User-Provided IDs Override

User-provided IDs always take precedence over file-based IDs:

```python
@parametrize_from_fixture("test_data.csv", ids=["custom_1", "custom_2"])
def test_with_override_ids(param1, param2):
    # Uses custom_1, custom_2 regardless of file content
    pass
```

### Explicit File Format

Override automatic format detection:

```python
@parametrize_from_fixture("data.txt", file_format="csv")
def test_explicit_format(param1, param2):
    # Treats data.txt as CSV regardless of extension
    pass
```

### Custom Fixtures Directory

Override the default fixtures directory:

```python
@parametrize_from_fixture("test_data.csv", fixtures_dir="custom/fixtures")
def test_custom_dir(param1, param2):
    # Looks in custom/fixtures/ instead of tests/fixtures/
    pass
```

## Integration with pytest.mark.parametrize

The decorator supports all `pytest.mark.parametrize` options:

```python
@parametrize_from_fixture(
    "test_data.csv",
    indirect=True,
    scope="class"
)
def test_with_pytest_options(param1, param2):
    # Uses indirect=True and scope="class"
    pass
```

## Error Handling

The decorator provides clear error messages for common issues:

- **File not found**: `FileNotFoundError: Fixture test_data.csv does not exist`
- **Invalid format**: `ValueError: Cannot auto-detect format for file: data.unknown`
- **Inconsistent data**: `ValueError: All items in JSON file must have the same keys`
- **Empty data**: `ValueError: CSV file has no data rows`

## Best Practices

1. **Use descriptive test IDs** that make it easy to identify failing tests
2. **Keep data files focused** - one file per logical test group
3. **Use consistent field names** across related test files
4. **Include edge cases** in your test data
5. **Validate your test data** - ensure it's well-formed and complete

## Migration from Manual Parametrization

### Before:

```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (3, 4, 7), 
    (5, 6, 11),
])
def test_addition(a, b, expected):
    assert a + b == expected
```

### After:

Create `addition_tests.csv`:
```csv
id,a,b,expected
case_1,1,2,3
case_2,3,4,7
case_3,5,6,11
```

Update test:
```python
@parametrize_from_fixture("addition_tests.csv")
def test_addition(a, b, expected):
    assert int(a) + int(b) == int(expected)
```

!!! warning

    Note that CSV files will be read as strings by default, so you will need to convert them to integers if you want to use them in your test.

### Benefits:

- External data is easier to maintain and review
- Non-developers can contribute test cases
- Test data can be generated programmatically
- Better separation of test logic and test data
- More descriptive test IDs for better debugging
