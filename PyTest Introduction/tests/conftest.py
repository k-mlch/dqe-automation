import os
import pytest
import pandas as pd

# Fixture to read the CSV file
@pytest.fixture(scope="session")
def path_to_file():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "src", "data", "data.csv")

@pytest.fixture(scope="session")
def read_csv(path_to_file):
    return pd.read_csv(path_to_file)

# Fixture to validate the schema of the file
@pytest.fixture(scope= "session")
def validate_schema():
    def validate_schema(actual_schema, expected_schema):
        return actual_schema == expected_schema
    return validate_schema

# Pytest hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(items):
    for item in items:
        if not list(item.iter_markers()):
            item.add_marker(pytest.mark.unmarked)