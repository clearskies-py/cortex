from typing import Self

from clearskies import Model
from clearskies.columns import Json, String

from clearskies_cortex.backends import CortexBackend


class CortexCatalogEntityType(Model):
    """Model for entities."""

    id_column_name: str = "type"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "catalog/definitions"

    name = String()
    description = String()
    schema = Json()
    source = String()
    type = String()
