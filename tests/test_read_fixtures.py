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
    temp_dir_file = temp_dir / "test.json"
    dictionary = {"test": "test"}
    temp_dir_file.write_text(json.dumps(dictionary))

    actual = read_json_fixture("test.json")
    assert actual == dictionary


def test_read_jsonl_fixture(read_jsonl_fixture, temp_dir):
    temp_dir_file = temp_dir / "test.jsonl"
    jsonl = [{"test": "test"}, {"test": "test2"}]
    with open(temp_dir_file, "w") as f:
        for item in jsonl:
            f.write(json.dumps(item) + "\n")

    actual = read_jsonl_fixture("test.jsonl")
    assert actual == jsonl


def test_read_fixture_with_custom_yaml_deserialize(read_fixture, temp_dir):
    temp_dir_file = temp_dir / "test.yaml"
    yaml_data = yaml.dump({"test": "test"})
    temp_dir_file.write_text(yaml_data)

    actual = read_fixture("test.yaml", deserialize=yaml.safe_load)
    assert actual == {"test": "test"}
