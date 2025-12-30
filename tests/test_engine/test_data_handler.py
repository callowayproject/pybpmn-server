"""Test cases for `data_handler.py`."""

import pytest

from pybpmn_server.engine.data_handler import get_and_create_data, get_data, merge_data


class TestAppendData:
    """Test cases for `append_data`."""

    def test_append_data_with_list_path_and_input_data(self):
        """Test: `append_data` should append input data to a list if the path ends in `[]`."""
        instance_data = {"root": {"items": []}}
        input_data = {"name": "test_item"}
        merge_data(instance_data, input_data, item=None, data_path="root.items[]")

        assert len(instance_data["root"]["items"]) == 1
        assert instance_data["root"]["items"][0] == {"name": "test_item"}

    def test_append_data_with_dict_input_and_no_path(self):
        """Test: `append_data` should merge input data into an existing dictionary when no specific path is provided."""
        instance_data = {"root": {"settings": {"theme": "light"}}}
        input_data = {"theme": "dark", "language": "en"}
        merge_data(instance_data, input_data, item=None, data_path="root.settings")

        assert instance_data["root"]["settings"]["theme"] == "dark"
        assert instance_data["root"]["settings"]["language"] == "en"

    def test_append_data_with_vars_prefix_and_token_update(self):
        """Test: `append_data` should update item.vars attributes when keys start with 'vars.'."""

        class FakeItem:
            def __init__(self):
                self.vars = {}

        instance_data = {}
        input_data = {"vars.test": "value"}
        item = FakeItem()
        merge_data(instance_data, input_data, item=item, data_path=None)

        assert "test" in item.vars
        assert item.vars["test"] == "value"

    def test_append_data_with_none_input_data(self):
        """Test: `append_data` should make no modifications when input_data is None."""
        instance_data = {"root": {"settings": {"theme": "light"}}}
        merge_data(instance_data, None, item=None, data_path="root.settings")

        assert instance_data["root"]["settings"] == {"theme": "light"}


class TestGetData:
    """Test cases for `get_data`."""

    def test_get_data_with_existing_path(self):
        """Test: `get_data` should retrieve data for a valid dot-delimited path."""
        instance_data = {"root": {"settings": {"theme": "light"}}}
        result = get_data(instance_data, "root.settings.theme")
        assert result == "light"

    def test_get_data_with_non_existing_path(self):
        """Test: `get_data` should return None for a non-existent path."""
        instance_data = {"root": {"settings": {"theme": "light"}}}
        result = get_data(instance_data, "root.settings.language")
        assert result is None

    def test_get_data_with_none_path(self):
        """Test: `get_data` should return the entire dictionary when path is None."""
        instance_data = {"root": {"settings": {"theme": "light"}}}
        result = get_data(instance_data, None)
        assert result == instance_data

    def test_get_data_with_empty_path(self):
        """Test: `get_data` should return the entire dictionary when path is empty."""
        instance_data = {"root": {"settings": {"theme": "light"}}}
        result = get_data(instance_data, "")
        assert result == instance_data

    def test_get_data_with_array_access_in_path(self):
        """Test: `get_data` should handle paths with '[]' for accessing arrays."""
        instance_data = {"root": {"items": [{"name": "item1"}, {"name": "item2"}]}}
        result = get_data(instance_data, "root.items[]")
        assert result == instance_data["root"]["items"]

    def test_get_data_with_non_dict_instance_data(self):
        """Test: `get_data` should return None if instance_data is not a dictionary."""
        instance_data = [{"key": "value"}]
        result = get_data(instance_data, "key")
        assert result is None


class TestGetAndCreateData:
    """Test cases for `get_and_create_data`."""

    def test_get_and_create_data_with_valid_path(self):
        """Test: `get_and_create_data` should create a nested dictionary for a valid dot-delimited path."""
        instance_data = {}
        result = get_and_create_data(instance_data, "root.settings.theme")
        assert result == {}
        assert "root" in instance_data
        assert "settings" in instance_data["root"]
        assert "theme" in instance_data["root"]["settings"]

    def test_get_and_create_data_with_existing_path(self):
        """Test: `get_and_create_data` should return existing nested data for a valid path."""
        instance_data = {"root": {"settings": {"theme": "light"}}}
        result = get_and_create_data(instance_data, "root.settings.theme")
        assert result == "light"

    def test_get_and_create_data_with_none_path(self):
        """Test: `get_and_create_data` should return the entire dictionary when path is None."""
        instance_data = {"root": {"settings": {"theme": "light"}}}
        result = get_and_create_data(instance_data, None)
        assert result == instance_data

    def test_get_and_create_data_with_empty_path(self):
        """Test: `get_and_create_data` should return the entire dictionary when path is empty."""
        instance_data = {"root": {"settings": {"theme": "light"}}}
        result = get_and_create_data(instance_data, "")
        assert result == instance_data

    def test_get_and_create_data_with_array_path(self):
        """Test: `get_and_create_data` should create an empty array if the path ends with '[]'."""
        instance_data = {}
        result = get_and_create_data(instance_data, "root.items[]", as_array=True)
        assert result == []
        assert "root" in instance_data
        assert "items" in instance_data["root"]
        assert isinstance(instance_data["root"]["items"], list)

    def test_get_and_create_data_with_partial_creation(self):
        """Test: `get_and_create_data` should create missing parts of the path as dictionaries."""
        instance_data = {"root": {"existing": {}}}
        result = get_and_create_data(instance_data, "root.new_path.sub_path")
        assert result == {}
        assert "new_path" in instance_data["root"]
        assert "sub_path" in instance_data["root"]["new_path"]
        assert isinstance(instance_data["root"]["new_path"]["sub_path"], dict)

    def test_get_and_create_data_with_no_target_object(self):
        """Test: `get_and_create_data` should create and assign structures even if the starting object is missing."""
        instance_data = {}
        result = get_and_create_data(instance_data, "level1.level2.level3", as_array=False)
        assert result == {}
        assert "level1" in instance_data
        assert "level2" in instance_data["level1"]
        assert "level3" in instance_data["level1"]["level2"]

    def test_get_and_create_data_with_invalid_instance_data(self):
        """Test: `get_and_create_data` should raise an error when instance_data is not a dictionary."""
        instance_data = []  # Invalid type
        with pytest.raises(TypeError):
            get_and_create_data(instance_data, "key.value")
