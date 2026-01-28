from typing import Any, Self

from clearskies import Column
from clearskies.query import Condition, Query

from clearskies_cortex.models import cortex_catalog_entity


class CortexCatalogEntityTeam(cortex_catalog_entity.CortexCatalogEntity):
    """
    Model for Cortex team entities.

    This model extends CortexCatalogEntity to specifically handle team-type entities
    in the Cortex catalog. Teams represent organizational units that own and manage
    services and other entities.

    The model automatically filters for team entities and includes nested fields for
    team members, owners, metadata, and hierarchy groups. It provides methods to
    navigate the team hierarchy.

    ```python
    from clearskies_cortex.models import CortexCatalogEntityTeam

    # Fetch all team entities
    teams = CortexCatalogEntityTeam()
    for team in teams.get_final_query():
        print(f"Team: {team.name}")

    # Get the top-level team in the hierarchy
    team = teams.find("tag=my-team")
    top_team = team.get_top_level_team()
    print(f"Top-level team: {top_team.name}")

    # Get the immediate parent team
    parent = team.get_parent()
    if parent.exists():
        print(f"Parent team: {parent.name}")
    ```
    """

    def get_final_query(self) -> Query:
        return (
            self.get_query()
            .add_where(Condition("types=team"))
            .add_where(Condition("include_nested_fields=team:members"))
            .add_where(Condition("include_owners=true"))
            .add_where(Condition("include_metadata=true"))
            .add_where(Condition("include_hierarchy_fields=groups"))
        )

    def get_top_level_team(self: Self) -> Self:
        """Get the upper team of this service if set."""
        hierarchy = self.parse_hierarchy()
        if hierarchy.parents:
            parent = hierarchy.parents[0]
            while parent.parents:
                parent = parent.parents[0]
            return self.as_query().find(f"tag={parent.tag}")
        return self.empty()

    def get_parent(self: Self) -> Self:
        """Get the first team of this service if set."""
        hierarchy = self.parse_hierarchy()
        if hierarchy.parents:
            team = hierarchy.parents[0]
            return self.as_query().find(f"tag={team.tag}")
        return self.empty()
