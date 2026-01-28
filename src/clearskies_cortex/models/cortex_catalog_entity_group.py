from typing import Self

from clearskies import Model
from clearskies.columns import Json, String

from clearskies_cortex.backends import CortexBackend


class CortexCatalogEntityGroup(Model):
    """
    Model for Cortex entity groups.

    This model represents groups associated with a specific catalog entity in Cortex.
    Groups are used to categorize and organize entities with key-value pairs.

    The model connects to the Cortex API endpoint `catalog/{entity_tag}/groups` to fetch
    group information for a specific entity.

    ```python
    from clearskies_cortex.models import CortexCatalogEntityGroup

    # Fetch groups for a specific entity
    groups = CortexCatalogEntityGroup()
    entity_groups = groups.where("entity_tag=my-service")
    for group in entity_groups:
        print(f"Group tag: {group.tag}")
    ```
    """

    id_column_name: str = "entity_tag"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "catalog/{entity_tag}/groups"

    """
    The tag identifier of the parent entity this group belongs to.
    """
    entity_tag = String()

    """
    JSON object containing the group tag information.
    """
    tag = Json()
