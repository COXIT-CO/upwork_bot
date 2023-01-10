import pytest
from ..notion.db_scraper import is_database_id_valid


class TestDatabaseId:
    @pytest.mark.parametrize(
        "test",
        [
            "91937806-1a95-42e4-a3c6-340d9e002a73",
            "919378061a9542e4a3c6340d9e002a73",
        ],
    )
    def test_valid_database_id(test):
        assert is_database_id_valid(test)

    @pytest.mark.parametrize(
        "test",
        [
            "ss144-efg3443-vdfgfg",  # string length isn't equal 32 or 36
            "this string contains spaces",
            "dfb@434-%jf63-&jhdf234",  # string contains wrong letters
        ],
    )
    def test_invalid_database_id(test):
        assert not is_database_id_valid(test)
