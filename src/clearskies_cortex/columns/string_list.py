from typing import Any

from clearskies.columns import String


class StringList(String):
    """Column type for comma delimited string."""

    def from_backend(self, value: str | list[str]) -> list[str]:
        """Return comma delimited string to list."""
        if isinstance(value, list):
            return value
        return value.split(",")

    def to_backend(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Make any changes needed to save the data to the backend.

        This typically means formatting changes - converting DateTime objects to database
        date strings, etc...
        """
        if self.name not in data:
            return data

        return {**data, self.name: str(",".join(data[self.name]))}
