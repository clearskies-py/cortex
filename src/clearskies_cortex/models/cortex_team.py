from typing import Self

from clearskies import Model
from clearskies.columns import (
    BelongsToModel,
    Boolean,
    CategoryTree,
    CategoryTreeAncestors,
    CategoryTreeChildren,
    CategoryTreeDescendants,
    Datetime,
    Json,
    String,
)

from clearskies_cortex.backends import CortexBackend
from clearskies_cortex.models import cortex_team_category_tree


class CortexTeam(Model):
    """
    Model for Cortex teams.

    This model represents teams in Cortex. Teams are organizational units that own and manage
    services and other entities. Teams support hierarchical relationships through parent-child
    connections.

    The model connects to the Cortex API endpoint `teams` and provides navigation through
    team hierarchies using CategoryTree relationships.

    ```python
    from clearskies_cortex.models import CortexTeam

    # Fetch all teams
    teams = CortexTeam()
    for team in teams:
        print(f"Team: {team.get_name()}")

    # Find a specific team
    team = teams.find("team_tag=my-team")

    # Navigate team hierarchy
    if team.has_parents():
        top_team = team.find_top_level_team()
        print(f"Top-level team: {top_team.get_name()}")

    if team.has_childeren():
        for child in team.children:
            print(f"Child team: {child.get_name()}")
    ```
    """

    id_column_name: str = "team_tag"

    backend = CortexBackend(
        api_to_model_map={
            "cortexTeam.members": "members",
        }
    )

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "teams"

    """
    The unique tag identifier for the team.
    """
    team_tag = String()

    """
    The tag of the catalog entity associated with this team.
    """
    catalog_entity_tag = String()

    """
    Whether the team is archived.
    """
    is_archived = Boolean()

    """
    CategoryTree relationship for parent team navigation.

    Uses CortexTeamCategoryTree to manage hierarchical team relationships.
    """
    parent_team_tag = CategoryTree(
        cortex_team_category_tree.CortexTeamCategoryTree,
        load_relatives_strategy="individual",
        tree_child_id_column_name="child_team_tag",
        tree_parent_id_column_name="parent_team_tag",
    )

    """
    The parent team model instance.
    """
    parent = BelongsToModel("parent_team_tag")

    """
    List of direct child teams.
    """
    children = CategoryTreeChildren("parent_team_tag")

    """
    List of all ancestor teams (from immediate parent to root).
    """
    ancestors = CategoryTreeAncestors("parent_team_tag")

    """
    List of all descendant teams (all children recursively).
    """
    descendants = CategoryTreeDescendants("parent_team_tag")

    """
    JSON object containing external links associated with the team.
    """
    links = Json()

    """
    JSON object containing custom metadata for the team.

    Includes the team name accessible via `get_name()`.
    """
    metadata = Json()

    """
    JSON object containing Slack channel configurations.
    """
    slack_channels = Json()

    """
    The type of team.
    """
    type = String()

    """
    JSON object containing team member information.
    """
    members = Json()

    """
    The unique identifier for the team.
    """
    id = String()

    """
    Timestamp of when the team was last updated.
    """
    last_updated = Datetime()

    """
    Search parameter: Include teams without members in results.
    """
    include_teams_without_members = Boolean(is_searchable=True, is_temporary=True)

    def get_name(self) -> str:
        """Retrieve name from metadata."""
        return str(self.metadata.get("name", "")) if self.metadata else ""

    def has_parents(self) -> bool:
        """Check if team has parents. If not it's a top-level team."""
        return len(self.ancestors) > 0

    def has_childeren(self) -> bool:
        """Check if team has child. If not it's a bottom-level team."""
        return len(self.children) > 0

    def find_top_level_team(self: Self) -> Self:
        """
        Find the top-level team of the team.

        If team not has parents, return itself.
        """
        return self if not self.has_parents() else self.ancestors[0]  # type: ignore[index]
