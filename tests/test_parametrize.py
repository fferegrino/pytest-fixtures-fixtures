"""Tests for parametrize_from_fixture decorator."""

import json

from pytest_fixtures_fixtures.parametrize import parametrize_from_fixture


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
