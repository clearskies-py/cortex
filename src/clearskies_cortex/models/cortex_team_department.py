from collections import OrderedDict
from typing import Any, Self

from clearskies import Model
from clearskies.columns import Json, String

from clearskies_cortex.backends import CortexBackend


class CortexTeamDepartment(Model):
    """Model for departments."""

    backend = CortexBackend()
    id_column_name: str = "department_tag"

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "teams/departments"

    department_tag = String()
    catalog_entity_tag = String()
    description = String()
    name = String()
    members = Json()
