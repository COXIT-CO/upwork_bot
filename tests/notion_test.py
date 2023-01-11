import pytest
from notion.db_scraper import is_database_id_valid, get_database_id_from_url


class TestDatabaseId:
    @pytest.mark.parametrize(
        "test",
        [
            "91937806-1a95-42e4-a3c6-340d9e002a73",
            "919378061a9542e4a3c6340d9e002a73",
        ],
    )
    def test_valid_database_id(self, test):
        assert is_database_id_valid(test)

    @pytest.mark.parametrize(
        "test",
        [
            "ss144-efg3443-vdfgfg",  # string length isn't equal 32 or 36
            "this string contains spaces",
            "dfb@434-%jf63-&jhdf234",  # string contains wrong letters
        ],
    )
    def test_invalid_database_id(self, test):
        assert not is_database_id_valid(test)


@pytest.mark.parametrize(
    "test",
    [
        "https://www.notion.so/6e0bdc477c8f4160a447ncb1f82218b3?v=d827154deef4430ba75fc82913e1d757",
        "https://www.notion.so/6e0b-dc47-7c8f41-60a447n-cb1f82218b3?v=d827154deef4430ba75fc82913e1d757",
        "this is invalid string, return it",
        "",
    ],
)
def test_get_database_id_from_url(test):
    if (
        test
        == "https://www.notion.so/6e0bdc477c8f4160a447ncb1f82218b3?v=d827154deef4430ba75fc82913e1d757"
    ):
        assert get_database_id_from_url(test) == "6e0bdc477c8f4160a447ncb1f82218b3"
    elif (
        test
        == "https://www.notion.so/6e0b-dc47-7c8f41-60a447n-cb1f82218b3?v=d827154deef4430ba75fc82913e1d757"
    ):
        assert get_database_id_from_url(test) == "6e0b-dc47-7c8f41-60a447n-cb1f82218b3"
    elif test == "this is invalid string that have to be just returned":
        assert get_database_id_from_url(test) == "this is invalid string, return it"
    elif test == "":
        assert get_database_id_from_url(test) == ""
