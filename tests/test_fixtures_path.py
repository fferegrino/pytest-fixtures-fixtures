import pytest


def test_default_fixtures_path_exists(fixtures_path):
    assert fixtures_path.exists()
    assert fixtures_path.is_dir()
    assert fixtures_path.name == "fixtures"
    assert fixtures_path.parent.name == "tests"
    assert len(list(fixtures_path.glob("*"))) == 1


def test_default_fixture_allow_non_existing_fixture(path_for_fixture):
    with pytest.raises(FileNotFoundError):
        path_for_fixture("test.txt")


class TestOverrideFixturesPath:
    @pytest.fixture
    def temp_dir(self, tmp_path):
        path = tmp_path / "fixtures"
        path.mkdir()
        return path

    @pytest.fixture
    def fixtures_path(self, temp_dir):
        return temp_dir

    def test_temp_dir_exists(self, fixtures_path, temp_dir):
        assert fixtures_path.exists()
        assert fixtures_path.is_dir()
        assert fixtures_path.name == "fixtures"
        assert fixtures_path == temp_dir

    def test_temp_dir_is_used(self, read_fixture, temp_dir):
        temp_dir_file = temp_dir / "test.txt"
        temp_dir_file.write_text("test")

        assert read_fixture("test.txt") == "test"
