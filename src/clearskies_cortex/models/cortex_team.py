from typing import Self, cast

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
    """Model for teams."""

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

    team_tag = String()
    catalog_entity_tag = String()
    is_archived = Boolean()
    parent_team_tag = CategoryTree(
        cortex_team_category_tree.CortexTeamCategoryTree,
        load_relatives_strategy="individual",
        tree_child_id_column_name="child_team_tag",
        tree_parent_id_column_name="parent_team_tag",
    )
    parent = BelongsToModel("parent_team_tag")
    children = CategoryTreeChildren("parent_team_tag")
    ancestors = CategoryTreeAncestors("parent_team_tag")
    descendants = CategoryTreeDescendants("parent_team_tag")
    links = Json()
    metadata = Json()
    slack_channels = Json()
    type = String()
    members = Json()
    id = String()
    last_updated = Datetime()

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
