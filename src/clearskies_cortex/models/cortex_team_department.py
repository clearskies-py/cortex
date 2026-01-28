from collections import OrderedDict
from typing import Any, Self

from clearskies import Model
from clearskies.columns import Json, String

from clearskies_cortex.backends import CortexBackend


class CortexTeamDepartment(Model):
    """
    Model for Cortex team departments.

    This model represents departments within teams in Cortex. Departments are organizational
    subdivisions within teams that can have their own members and descriptions.

    The model connects to the Cortex API endpoint `teams/departments` to fetch department data.

    ```python
    from clearskies_cortex.models import CortexTeamDepartment

    # Fetch all departments
    departments = CortexTeamDepartment()
    for dept in departments:
        print(f"Department: {dept.name}")
        print(f"Description: {dept.description}")
    ```
    """

    backend = CortexBackend()
    id_column_name: str = "department_tag"

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "teams/departments"

    """
    The unique tag identifier for the department.
    """
    department_tag = String()

    """
    The tag of the catalog entity associated with this department.
    """
    catalog_entity_tag = String()

    """
    A description of the department's purpose and responsibilities.
    """
    description = String()

    """
    The human-readable name of the department.
    """
    name = String()

    """
    JSON object containing department member information.
    """
    members = Json()
