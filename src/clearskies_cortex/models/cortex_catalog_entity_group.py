from typing import Self

from clearskies import Model
from clearskies.columns import Json, String

from clearskies_cortex.backends import CortexBackend


class CortexCatalogEntityGroup(Model):
    """Model for teams."""

    id_column_name: str = "entity_tag"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "catalog/{entity_tag}/groups"

    entity_tag = String()
    tag = Json()
