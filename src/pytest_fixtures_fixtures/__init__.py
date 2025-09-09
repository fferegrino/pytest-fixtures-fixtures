"""Handy fixtures to access your fixtures."""

from .parametrize import parametrize_from_fixture
from .protocols import (
    FixturePath,
    ReadCsvDictFixture,
    ReadCsvFixture,
    ReadFixture,
    ReadJsonFixture,
    ReadJsonlFixture,
    ReadYamlFixture,
)

__version__ = "0.3.3"

__all__ = [
    "parametrize_from_fixture",
    "FixturePath",
    "ReadFixture",
    "ReadJsonFixture",
    "ReadJsonlFixture",
    "ReadCsvFixture",
    "ReadCsvDictFixture",
    "ReadYamlFixture",
]
