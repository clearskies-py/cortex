from typing import Self, cast

from clearskies import Model
from clearskies.columns import (
    BelongsToModel,
    Boolean,
    CategoryTree,
    CategoryTreeAncestors,
    CategoryTreeChildren,
    Json,
    String,
)

from clearskies_cortex.backends import CortexBackend
from clearskies_cortex.models import cortex_team_category_tree


class CortexTeam(Model):
    """Model for teams."""

    id_column_name: str = "team_tag"

    backend = CortexBackend()

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
    links = Json()
    metadata = Json()
    slack_channels = Json()
    type = String()
    cortex_team = Json()
    id = String()

    def get_name(self) -> str:
        """Retrieve name from metadata."""
        return str(self.metadata.get("name", "")) if self.metadata else ""

    def is_domain(self) -> bool:
        """Check if team has parents. If not it's a domain."""
        return not len(self.ancestors)

    def is_squad(self) -> bool:
        """Check if team has child. If not it's a squad."""
        return not len(self.children)

    def find_domain(self: Self) -> "CortexTeam":
        """
        Find the domain of the team.

        If team is the domain, return itself.
        """
        return self if self.is_domain() else cast(Self, self.ancestors.first())
