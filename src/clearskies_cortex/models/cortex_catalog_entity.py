from collections.abc import Iterator
from typing import Self

from clearskies import Model
from clearskies.columns import Boolean, Datetime, HasMany, Json, String
from clearskies.query import Query

from clearskies_cortex.backends import CortexBackend
from clearskies_cortex.columns import StringList
from clearskies_cortex.models import cortex_catalog_entity_group, cortex_catalog_entity_scorecard


class CortexCatalogEntity(Model):
    """Model for entities."""

    id_column_name: str = "tag"

    backend = CortexBackend()

    @classmethod
    def destination_name(cls: type[Self]) -> str:
        """Return the slug of the api endpoint for this model."""
        return "catalog"

    id = String()
    tag = String()
    groups = StringList("groups")
    owners = Json()
    ownership = Json()
    ownersV2 = Json()
    description = String()
    git = Json()
    hierarchy = Json()
    last_updated = Datetime()
    is_archived = Boolean()
    links = Json()
    members = Json()
    metadata = Json()
    slack_channels = Json()
    name = String()
    type = String()
    scorecards = HasMany(
        cortex_catalog_entity_scorecard.CortexCatalogEntityScorecard,
        foreign_column_name="entity_tag",
    )
    group_models = HasMany(
        cortex_catalog_entity_group.CortexCatalogEntityGroup,
        foreign_column_name="entity_tag",
    )

    # search columns
    hierarchy_depth = String(is_searchable=True, is_temporary=True)
    git_repositories = StringList(is_searchable=True, is_temporary=True)
    types = StringList(is_searchable=True, is_temporary=True)
    query = String(is_searchable=True, is_temporary=True)
    include_archived = Boolean(is_searchable=True, is_temporary=True)
    include_metadata = Boolean(is_searchable=True, is_temporary=True)
    include_links = Boolean(is_searchable=True, is_temporary=True)
    include_owners = Boolean(is_searchable=True, is_temporary=True)
    include_nested_fields = StringList(is_searchable=True, is_temporary=True)
    include_hierarchy_fields = StringList(is_searchable=True, is_temporary=True)

    def parse_groups(self) -> dict[str, str]:
        """
        Parse the strings of groups.

        The groups is a list of string with key,value splitted by ':'.
        Return a dict with key value.
        """
        parsed: dict[str, str] = {}
        if self.groups:
            for entity in self.groups:
                splitted = entity.split(":")
                if len(splitted) > 1:
                    parsed[splitted[0]] = splitted[1]
        return parsed
