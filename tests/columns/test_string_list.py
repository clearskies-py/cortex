import unittest

from clearskies_cortex.columns import StringList


class TestStringList(unittest.TestCase):
    """Tests for the StringList column type."""

    def test_from_backend_with_string(self):
        """Test converting a comma-delimited string to a list."""
        column = StringList()
        column.name = "tags"

        result = column.from_backend("tag1,tag2,tag3")

        self.assertEqual(result, ["tag1", "tag2", "tag3"])

    def test_from_backend_with_single_value(self):
        """Test converting a single value string to a list."""
        column = StringList()
        column.name = "tags"

        result = column.from_backend("single-tag")

        self.assertEqual(result, ["single-tag"])

    def test_from_backend_with_empty_string(self):
        """Test converting an empty string to a list."""
        column = StringList()
        column.name = "tags"

        result = column.from_backend("")

        self.assertEqual(result, [""])

    def test_from_backend_with_list(self):
        """Test that a list input is returned as-is."""
        column = StringList()
        column.name = "tags"

        result = column.from_backend(["tag1", "tag2", "tag3"])

        self.assertEqual(result, ["tag1", "tag2", "tag3"])

    def test_from_backend_with_empty_list(self):
        """Test that an empty list input is returned as-is."""
        column = StringList()
        column.name = "tags"

        result = column.from_backend([])

        self.assertEqual(result, [])

    def test_from_backend_with_none(self):
        """Test that None input returns an empty list."""
        column = StringList()
        column.name = "tags"

        result = column.from_backend(None)

        self.assertEqual(result, [])

    def test_to_backend_with_list(self):
        """Test converting a list to a comma-delimited string."""
        column = StringList()
        column.name = "tags"

        data = {"tags": ["tag1", "tag2", "tag3"]}
        result = column.to_backend(data)

        self.assertEqual(result["tags"], "tag1,tag2,tag3")

    def test_to_backend_with_single_item_list(self):
        """Test converting a single-item list to a string."""
        column = StringList()
        column.name = "tags"

        data = {"tags": ["single-tag"]}
        result = column.to_backend(data)

        self.assertEqual(result["tags"], "single-tag")

    def test_to_backend_with_empty_list(self):
        """Test converting an empty list to a string."""
        column = StringList()
        column.name = "tags"

        data = {"tags": []}
        result = column.to_backend(data)

        self.assertEqual(result["tags"], "")

    def test_to_backend_preserves_other_fields(self):
        """Test that to_backend preserves other fields in the data dict."""
        column = StringList()
        column.name = "tags"

        data = {"tags": ["tag1", "tag2"], "name": "test", "id": 123}
        result = column.to_backend(data)

        self.assertEqual(result["tags"], "tag1,tag2")
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["id"], 123)

    def test_to_backend_without_column_in_data(self):
        """Test that to_backend returns data unchanged if column not present."""
        column = StringList()
        column.name = "tags"

        data = {"name": "test", "id": 123}
        result = column.to_backend(data)

        self.assertEqual(result, {"name": "test", "id": 123})
        self.assertNotIn("tags", result)

    def test_to_backend_does_not_mutate_original(self):
        """Test that to_backend doesn't mutate the original data dict."""
        column = StringList()
        column.name = "tags"

        original_list = ["tag1", "tag2"]
        data = {"tags": original_list}
        result = column.to_backend(data)

        # Original data should be unchanged
        self.assertEqual(data["tags"], ["tag1", "tag2"])
        # Result should have the converted string
        self.assertEqual(result["tags"], "tag1,tag2")

    def test_from_backend_with_whitespace(self):
        """Test that whitespace is preserved in values."""
        column = StringList()
        column.name = "tags"

        result = column.from_backend("tag 1, tag 2 , tag 3")

        # Whitespace is preserved (not trimmed)
        self.assertEqual(result, ["tag 1", " tag 2 ", " tag 3"])

    def test_from_backend_with_special_characters(self):
        """Test handling of special characters in values."""
        column = StringList()
        column.name = "tags"

        result = column.from_backend("team:platform,env:production,version:1.0")

        self.assertEqual(result, ["team:platform", "env:production", "version:1.0"])

    def test_roundtrip_conversion(self):
        """Test that converting to backend and back preserves data."""
        column = StringList()
        column.name = "tags"

        original = ["tag1", "tag2", "tag3"]
        data = {"tags": original}

        # Convert to backend format
        backend_data = column.to_backend(data)
        self.assertEqual(backend_data["tags"], "tag1,tag2,tag3")

        # Convert back from backend format
        restored = column.from_backend(backend_data["tags"])
        self.assertEqual(restored, original)


if __name__ == "__main__":
    unittest.main()
