import pytest


def test_default_fixtures_path_exists(fixtures_path):
    """Test default fixtures path exists."""
    assert fixtures_path.exists()
    assert fixtures_path.is_dir()
    assert fixtures_path.name == "fixtures"
    assert fixtures_path.parent.name == "tests"
    assert len(list(fixtures_path.glob("*"))) == 1


def test_default_fixture_fails_on_non_existing_fixture(path_for_fixture):
    """Test default fixture fails on non existing fixture."""
    with pytest.raises(FileNotFoundError):
        path_for_fixture("test.txt")


def test_path_for_fixture_must_exist_false(path_for_fixture):
    """Test path_for_fixture with must_exist=False doesn't raise error."""
    # Should not raise FileNotFoundError even if file doesn't exist
    path = path_for_fixture("nonexistent.txt", must_exist=False)
    assert path.name == "nonexistent.txt"
    assert not path.exists()


def test_path_for_fixture_nonexistent_nested(path_for_fixture):
    """Test path_for_fixture with nonexistent nested path."""
    with pytest.raises(FileNotFoundError):
        path_for_fixture("nonexistent", "nested", "file.txt")


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
        """Test temp_dir exists."""
        assert fixtures_path.exists()
        assert fixtures_path.is_dir()
        assert fixtures_path.name == "fixtures"
        assert fixtures_path == temp_dir

    def test_temp_dir_is_used(self, read_fixture, temp_dir):
        """Test temp_dir is used."""
        temp_dir_file = temp_dir / "test.txt"
        temp_dir_file.write_text("test")

        assert read_fixture("test.txt") == "test"

    def test_path_for_fixture_multiple_components(self, path_for_fixture):
        """Test path_for_fixture with multiple path components."""
        # Create nested directory structure
        fixtures_path = path_for_fixture("test.txt", must_exist=False).parent  # Get the fixtures directory
        nested_dir = fixtures_path / "data" / "subdir"
        nested_dir.mkdir(parents=True)
        test_file = nested_dir / "test.txt"
        test_file.write_text("test content")

        # Test with multiple components
        path = path_for_fixture("data", "subdir", "test.txt")
        assert path == test_file
        assert path.exists()

    def test_path_for_fixture_with_pathlike(self, path_for_fixture):
        """Test path_for_fixture with PathLike objects."""
        from pathlib import Path

        fixtures_path = path_for_fixture("test.txt", must_exist=False).parent  # Get the fixtures directory
        test_file = fixtures_path / "test.txt"
        test_file.write_text("test")

        # Test with Path object
        path = path_for_fixture(Path("test.txt"))
        assert path == test_file
        assert path.exists()
