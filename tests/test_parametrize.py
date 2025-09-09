"""Tests for parametrize_from_fixture decorator."""

import json
import os
from unittest.mock import patch

from pytest_fixtures_fixtures.parametrize import _get_fixtures_path, parametrize_from_fixture


def assert_all_ints(*value):
    assert all(isinstance(v, int) for v in value)


@parametrize_from_fixture("it_is_a_csv.xyz", file_format="csv")
def test_explicit_format(a, b, c):
    """Test parametrization with explicit file format."""
    assert int(a) + int(b) == int(c)


class TestFilesWithIds:
    @parametrize_from_fixture("test_data.csv")
    def test_sum_three_numbers_csv_with_ids(self, a, b, c):
        assert int(a) + int(b) == int(c)

    @parametrize_from_fixture("test_data.json")
    def test_sum_three_numbers_json_with_ids(self, a, b, c):
        """Test parametrization from JSON file with IDs."""
        assert_all_ints(a, b, c)
        assert a + b == c

    @parametrize_from_fixture("test_data.yaml")
    def test_sum_three_numbers_yaml_with_ids(self, a, b, c):
        """Test parametrization from YAML file with IDs."""
        assert_all_ints(a, b, c)
        assert a + b == c

    @parametrize_from_fixture("test_data.jsonl")
    def test_sum_three_numbers_jsonl_with_ids(self, a, b, c):
        """Test parametrization from JSONL file with IDs."""
        assert_all_ints(a, b, c)
        assert a + b == c


class TestFilesWithoutIds:
    @parametrize_from_fixture("no_id_data.csv")
    def test_sum_three_numbers_csv_no_ids(self, a, b, c):
        assert int(a) + int(b) == int(c)

    @parametrize_from_fixture("no_id_data.json")
    def test_sum_three_numbers_json_no_ids(self, a, b, c):
        """Test parametrization from JSON file without IDs."""
        assert_all_ints(a, b, c)
        assert a + b == c

    @parametrize_from_fixture("no_id_data.yaml")
    def test_sum_three_numbers_yaml_no_ids(self, a, b, c):
        """Test parametrization from YAML file with IDs."""
        assert_all_ints(a, b, c)
        assert a + b == c

    @parametrize_from_fixture("no_id_data.jsonl")
    def test_sum_three_numbers_jsonl_no_ids(self, a, b, c):
        """Test parametrization from JSONL file with IDs."""
        assert_all_ints(a, b, c)
        assert a + b == c


@parametrize_from_fixture("test_data.csv", ids=["user_id_1", "user_id_2", "user_id_3"])
def test_user_ids_override_file_ids(a, b, c):
    """Test that user-provided IDs override file IDs."""
    assert int(a) + int(b) == int(c)


class TestHelperReaderFunctions:
    # Unit tests for helper functions with ID support
    def test_read_csv_for_parametrize_with_ids(self, tmp_path):
        """Test _read_csv_for_parametrize function with ID column."""
        from pytest_fixtures_fixtures.parametrize import _read_csv_for_parametrize

        # Create test CSV file with ID column
        csv_file = tmp_path / "test_with_ids.csv"
        csv_content = "id,name,age\ntest_alice,Alice,30\ntest_bob,Bob,25"
        csv_file.write_text(csv_content)

        param_names, param_values, test_ids = _read_csv_for_parametrize(csv_file, "utf-8")

        assert param_names == "name,age"
        assert param_values == [("Alice", "30"), ("Bob", "25")]
        assert test_ids == ["test_alice", "test_bob"]

    def test_read_csv_for_parametrize_without_ids(self, tmp_path):
        """Test _read_csv_for_parametrize function without ID column."""
        from pytest_fixtures_fixtures.parametrize import _read_csv_for_parametrize

        # Create test CSV file without ID column
        csv_file = tmp_path / "test_no_ids.csv"
        csv_content = "name,age\nAlice,30\nBob,25"
        csv_file.write_text(csv_content)

        param_names, param_values, test_ids = _read_csv_for_parametrize(csv_file, "utf-8")

        assert param_names == "name,age"
        assert param_values == [("Alice", "30"), ("Bob", "25")]
        assert test_ids is None

    def test_read_json_for_parametrize_with_ids(self, tmp_path):
        """Test _read_json_for_parametrize function with ID key."""
        from pytest_fixtures_fixtures.parametrize import _read_json_for_parametrize

        # Create test JSON file with ID keys
        json_file = tmp_path / "test_with_ids.json"
        data = [{"id": "test_case_1", "x": 1, "y": 2}, {"id": "test_case_2", "x": 3, "y": 4}]
        json_file.write_text(json.dumps(data))

        param_names, param_values, test_ids = _read_json_for_parametrize(json_file, "utf-8")

        assert param_names == "x,y"
        assert param_values == [(1, 2), (3, 4)]
        assert test_ids == ["test_case_1", "test_case_2"]

    def test_read_json_for_parametrize_without_ids(self, tmp_path):
        """Test _read_json_for_parametrize function without ID key."""
        from pytest_fixtures_fixtures.parametrize import _read_json_for_parametrize

        # Create test JSON file without ID keys
        json_file = tmp_path / "test_no_ids.json"
        data = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
        json_file.write_text(json.dumps(data))

        param_names, param_values, test_ids = _read_json_for_parametrize(json_file, "utf-8")

        assert param_names == "x,y"
        assert param_values == [(1, 2), (3, 4)]
        assert test_ids is None

    def test_read_jsonl_for_parametrize_with_ids(self, tmp_path):
        """Test _read_jsonl_for_parametrize function with ID key."""
        from pytest_fixtures_fixtures.parametrize import _read_jsonl_for_parametrize

        # Create test JSONL file with ID keys
        jsonl_file = tmp_path / "test_with_ids.jsonl"
        lines = ['{"id": "jsonl_1", "status": "ok"}', '{"id": "jsonl_2", "status": "error"}']
        jsonl_file.write_text("\n".join(lines))

        param_names, param_values, test_ids = _read_jsonl_for_parametrize(jsonl_file, "utf-8")

        assert param_names == "status"
        assert param_values == [("ok",), ("error",)]
        assert test_ids == ["jsonl_1", "jsonl_2"]

    def test_read_yaml_for_parametrize_with_ids(self, tmp_path):
        """Test _read_yaml_for_parametrize function with ID key."""
        import yaml

        from pytest_fixtures_fixtures.parametrize import _read_yaml_for_parametrize

        # Create test YAML file with ID keys
        yaml_file = tmp_path / "test_with_ids.yaml"
        data = [{"id": "yaml_1", "name": "Alice"}, {"id": "yaml_2", "name": "Bob"}]
        yaml_file.write_text(yaml.dump(data))

        param_names, param_values, test_ids = _read_yaml_for_parametrize(yaml_file, "utf-8")

        assert param_names == "name"
        assert param_values == [("Alice",), ("Bob",)]
        assert test_ids == ["yaml_1", "yaml_2"]


class TestGetFixturesPath:
    """Test the _get_fixtures_path function with various configurations."""

    def test_explicit_fixtures_dir_parameter(self, tmp_path):
        """Test that explicit fixtures_dir parameter takes precedence."""
        custom_path = tmp_path / "custom_fixtures"
        custom_path.mkdir()

        with patch.dict(os.environ, {"PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE": str(tmp_path / "env_fixtures")}):
            result = _get_fixtures_path(fixtures_dir=str(custom_path))
            assert result == custom_path.resolve()

    def test_environment_variable_when_no_param(self, tmp_path):
        """Test that environment variable is used when no fixtures_dir parameter is provided."""
        env_path = tmp_path / "env_fixtures"
        env_path.mkdir()

        with patch.dict(os.environ, {"PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE": str(env_path)}):
            result = _get_fixtures_path()
            assert result == env_path.resolve()

    def test_environment_variable_with_relative_path(self, tmp_path, monkeypatch):
        """Test that environment variable works with relative paths."""
        # Change to tmp_path directory
        monkeypatch.chdir(tmp_path)

        # Create relative path
        rel_path = "custom/fixtures"
        full_path = tmp_path / "custom" / "fixtures"
        full_path.mkdir(parents=True)

        with patch.dict(os.environ, {"PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE": rel_path}):
            result = _get_fixtures_path()
            assert result == full_path.resolve()

    def test_default_path_when_no_config(self, tmp_path, monkeypatch):
        """Test that default path is used when no configuration is provided."""
        # Change to tmp_path directory
        monkeypatch.chdir(tmp_path)

        # Create default fixtures directory
        default_path = tmp_path / "tests" / "fixtures"

        # Ensure environment variable is not set
        with patch.dict(os.environ, {}, clear=True):
            result = _get_fixtures_path()
            assert result == default_path

    def test_pathlib_path_parameter(self, tmp_path):
        """Test that Path objects work as fixtures_dir parameter."""
        custom_path = tmp_path / "pathlib_fixtures"
        custom_path.mkdir()

        result = _get_fixtures_path(fixtures_dir=custom_path)
        assert result == custom_path.resolve()

    def test_environment_variable_overrides_default_but_not_param(self, tmp_path):
        """Test precedence: explicit param > env var > default."""
        # Setup paths
        param_path = tmp_path / "param_fixtures"
        env_path = tmp_path / "env_fixtures"
        param_path.mkdir()
        env_path.mkdir()

        # Test that env var overrides default
        with patch.dict(os.environ, {"PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE": str(env_path)}):
            result_env_only = _get_fixtures_path()
            assert result_env_only == env_path.resolve()

            # Test that param overrides env var
            result_param_over_env = _get_fixtures_path(fixtures_dir=str(param_path))
            assert result_param_over_env == param_path.resolve()


class TestParametrizeWithCustomFixturesPath:
    """Integration tests for parametrize_from_fixture with custom fixtures paths."""

    def test_parametrize_with_environment_variable(self, tmp_path):
        """Test that parametrization works with custom fixtures path from environment variable."""
        # Create custom fixtures directory and file
        custom_fixtures = tmp_path / "my_custom_fixtures"
        custom_fixtures.mkdir()

        test_file = custom_fixtures / "custom_test_data.csv"
        test_file.write_text("a,b,c\n1,2,3\n4,5,9\n")

        # Set environment variable
        with patch.dict(os.environ, {"PYTEST_FIXTURES_FIXTURES_PATH_PARAMETRIZE": str(custom_fixtures)}):
            # Create a test function with the decorator
            @parametrize_from_fixture("custom_test_data.csv")
            def test_custom_path(a, b, c):
                assert int(a) + int(b) == int(c)

            # The decorator should have been applied successfully
            # Check that the test function has the parametrize mark
            assert hasattr(test_custom_path, "pytestmark")
            marks = test_custom_path.pytestmark
            parametrize_marks = [mark for mark in marks if mark.name == "parametrize"]
            assert len(parametrize_marks) == 1

            # Check the parameter values
            mark = parametrize_marks[0]
            assert mark.kwargs["argnames"] == "a,b,c"
            assert mark.kwargs["argvalues"] == [("1", "2", "3"), ("4", "5", "9")]

    def test_parametrize_with_explicit_fixtures_dir(self, tmp_path):
        """Test that parametrization works with explicit fixtures_dir parameter."""
        # Create custom fixtures directory and file
        custom_fixtures = tmp_path / "explicit_fixtures"
        custom_fixtures.mkdir()

        test_file = custom_fixtures / "explicit_test_data.json"
        test_data = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
        test_file.write_text(json.dumps(test_data))

        # Create a test function with explicit fixtures_dir
        @parametrize_from_fixture("explicit_test_data.json", fixtures_dir=str(custom_fixtures))
        def test_explicit_path(x, y):
            assert isinstance(x, int)
            assert isinstance(y, int)

        # Check that the decorator was applied successfully
        assert hasattr(test_explicit_path, "pytestmark")
        marks = test_explicit_path.pytestmark
        parametrize_marks = [mark for mark in marks if mark.name == "parametrize"]
        assert len(parametrize_marks) == 1

        # Check the parameter values
        mark = parametrize_marks[0]
        assert mark.kwargs["argnames"] == "x,y"
        assert mark.kwargs["argvalues"] == [(1, 2), (3, 4)]
