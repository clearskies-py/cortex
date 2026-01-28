import uuid
from collections import OrderedDict
from typing import Any, Iterator, Self

from clearskies import Model
from clearskies.columns import Boolean, Integer, String, Uuid

from clearskies_cortex.backends import CortexBackend, CortexTeamRelationshipBackend


class CortexTeamCategoryTree(Model):
    """
    Model for Cortex team hierarchy relationships.

    This model represents the hierarchical relationships between teams in Cortex.
    It is used internally by the CategoryTree column type to manage parent-child
    team relationships.

    The model connects to the Cortex API endpoint `teams/relationships` using the
    CortexTeamRelationshipBackend to transform the API response into a format
    suitable for clearskies CategoryTree operations.

    ```python
    from clearskies_cortex.models import CortexTeamCategoryTree

    # This model is typically used internally by CortexTeam
    # Direct usage example:
    tree = CortexTeamCategoryTree()
    relationships = tree.where("parent_team_tag=my-parent-team")
    for rel in relationships:
        print(f"Child: {rel.child_team_tag}, Level: {rel.level}")
    ```
    """

    id_column_name: str = "id"

    backend = CortexTeamRelationshipBackend(CortexBackend())

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "teams/relationships"

    """
    Unique identifier for the relationship record.
    """
    id = Uuid()

    """
    The tag of the parent team in the relationship.
    """
    parent_team_tag = String()

    """
    The tag of the child team in the relationship.
    """
    child_team_tag = String()

    """
    Whether this record represents a parent relationship.
    """
    is_parent = Boolean()

    """
    The depth level in the hierarchy (0 for direct parent/child).
    """
    level = Integer()
