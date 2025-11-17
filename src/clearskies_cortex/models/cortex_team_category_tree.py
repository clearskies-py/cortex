import uuid
from collections import OrderedDict
from typing import Any, Iterator, Self

from clearskies import Model
from clearskies.columns import Boolean, Integer, String, Uuid

from clearskies_cortex.backends import CortexBackend, CortexTeamRelationshipBackend


class CortexTeamCategoryTree(Model):
    """Model for teams."""

    id_column_name: str = "id"

    backend = CortexTeamRelationshipBackend(CortexBackend())

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "teams/relationships"

    id = Uuid()
    parent_team_tag = String()
    child_team_tag = String()
    is_parent = Boolean()
    level = Integer()
