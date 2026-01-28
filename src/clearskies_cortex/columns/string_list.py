from typing import Any

from clearskies.columns import String


class StringList(String):
    """
    Column type for comma-delimited string lists.

    This column type extends the String column to handle values that are stored as
    comma-delimited strings but should be represented as Python lists. It automatically
    converts between the two formats when reading from and writing to the backend.

    Use this column type when the API returns or expects comma-separated values that
    you want to work with as lists in your application code.

    ```python
    from clearskies import Model
    from clearskies_cortex.columns import StringList


    class MyModel(Model):
        # Define a column that stores ["tag1", "tag2"] as "tag1,tag2"
        tags = StringList()


    # When reading from the backend:
    # API returns: {"tags": "tag1,tag2,tag3"}
    # Model provides: model.tags = ["tag1", "tag2", "tag3"]

    # When writing to the backend:
    # Model has: model.tags = ["tag1", "tag2", "tag3"]
    # API receives: {"tags": "tag1,tag2,tag3"}
    ```
    """

    def from_backend(self, value: str | list[str]) -> list[str]:
        """
        Convert backend value to a Python list.

        Handles both string (comma-delimited) and list inputs for flexibility.

        Args:
            value: Either a comma-delimited string or a list of strings.

        Returns:
            A list of strings.
        """
        if isinstance(value, list):
            return value
        return value.split(",")

    def to_backend(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Convert Python list to comma-delimited string for backend storage.

        Transforms the list value back into a comma-separated string format
        expected by the backend API.

        Args:
            data: Dictionary containing the column data.

        Returns:
            Dictionary with the column value converted to a comma-delimited string.
        """
        if self.name not in data:
            return data

        return {**data, self.name: str(",".join(data[self.name]))}
