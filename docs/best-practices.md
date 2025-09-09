# Best Practices

This is a guide to help you write better tests with `pytest-fixtures-fixtures`.

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
