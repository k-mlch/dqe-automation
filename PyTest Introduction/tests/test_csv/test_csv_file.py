import pytest
import re

def test_file_not_empty(read_csv):
    assert not read_csv.empty, "CSV file is empty"

@pytest.mark.validate_csv
@pytest.mark.xfail(reason = "Known bug in the code")
def test_duplicates(read_csv):
    assert read_csv.duplicated().any() == False, "Duplicated rows are found"

@pytest.mark.validate_csv
def test_validate_schema(read_csv, validate_schema):
    expected_schema = ['id', 'name', 'age', 'email', 'is_active']
    actual_schema = read_csv.columns.tolist()
    assert validate_schema(actual_schema, expected_schema), f"Schema mismatch: expected {expected_schema}, actual {actual_schema}"

@pytest.mark.validate_csv
@pytest.mark.skip(reason = "This test is temporarily disabled.")
def test_age_column_valid(read_csv):
    assert read_csv['age'].min() >= 0 and read_csv['age'].max() <= 100, "Age column contains invalid values"


@pytest.mark.validate_csv
def test_email_column_valid(read_csv):
    email_pattern = re.compile(r".+\..+@.+\..+")
    for email in read_csv["email"]:
        assert email_pattern.match(email), f"Invalid email is found: {email}"

@pytest.mark.parametrize("id, is_active_expected", [
    (1, False),
    (2, True)
])
def test_active_players(read_csv, id, is_active_expected):
    player = read_csv[read_csv["id"] == id]
    player_is_active = player["is_active"].values[0]
    assert player_is_active == is_active_expected, f"Player with id = {id} has incorrect 'is_active' value"

def test_active_player(read_csv):
    player = read_csv[read_csv["id"] == 2]
    player_is_active = player["is_active"].values[0]
    assert player_is_active == True, "Player with id = 2 has incorrect 'is_active' value"
