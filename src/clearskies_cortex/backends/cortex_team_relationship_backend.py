import json
import logging
import uuid
from types import SimpleNamespace
from typing import Any

from clearskies import Configurable, Model, configs
from clearskies.backends.memory_backend import MemoryBackend, MemoryTable
from clearskies.columns import String, Uuid
from clearskies.di import inject
from clearskies.query import Condition, Query
from clearskies.query.result import RecordsQueryResult

from clearskies_cortex.backends import cortex_backend as rest_backend


class CortexTeamRelationshipBackend(MemoryBackend, Configurable):
    """Backend for Cortex.io."""

    logger = logging.getLogger(__name__)
    di = inject.Di()

    cortex_backend = configs.Any(default=None)
    _cached_teams: dict[str, dict[str, Any]]

    def __init__(
        self,
        cortex_backend,
        silent_on_missing_tables=True,
    ):
        super().__init__(silent_on_missing_tables)
        # This backend has its dependencies injected automatically because it is attachd to the model,
        # but when you directly instantiate the CortexBackend and pass it in, the di system never has a chance
        # to provide IT with the necessary deendencies.  Therefore, we just have to explicitly do it,
        # or we need to let the di system build the CortexBackend.  This change does both:
        self.cortex_backend = cortex_backend

    def records(self, query: Query) -> RecordsQueryResult:
        """Accept either a model or a model class and creates a "table" for it."""
        table_name = query.model_class.destination_name()
        if table_name not in self._tables:
            self._tables[table_name] = MemoryTable(query.model_class)
            [records, id_index] = self._fetch_and_map_relationship_data(table_name)
            # directly setting internal things is bad, but the create function on the MemoryTable
            # (which is how we _should_ feed data into it) does a lot of extra data validation that
            # we don't need since we built the data ourselves.  In short, it will be a lot slower, so I cheat.
            self._tables[table_name]._rows = records  # type: ignore[assignment]
            self._tables[table_name]._id_index = id_index  # type: ignore[assignment]
        return super().records(query)

    def _fetch_and_map_relationship_data(self, table_name: str) -> tuple[list[dict[str, str | int]], dict[str, int]]:
        class RelationshipModel(Model):
            id_column_name: str = "id"
            backend = rest_backend.CortexBackend()

            id = String()
            child_team_tag = String()
            parent_team_tag = String()
            provider = String()

            @classmethod
            def destination_name(cls) -> str:
                return "teams/relationships"

        # we need to map this to the kind of row structure expected by the category_tree column
        # (see https://github.com/clearskies-py/clearskies/blob/main/src/clearskies/columns/category_tree.py)
        # This takes slightly more time up front but makes for quick lookups in both directions (and we'll
        # cache the result so it only has to happen once).  The trouble is that we need to know the tree before
        # we can get started.  We want to start at the top or the bottom, but Cortex gives us neither.
        # therefore, we'll search for the root categories and then start over.  While we find those, we'll
        # convert from a list of edges to a dictionary of parent/children

        # Fetch all teams and filter out archived ones
        from clearskies_cortex.models.cortex_team import CortexTeam

        root_categories: dict[str, str] = {}
        known_children: dict[str, str] = {}
        relationships: dict[str, set[str]] = {}
        for relationship in (
            self._get_cortex_backend()
            .records(
                Query(
                    model_class=RelationshipModel,
                ),
            )
            .records
        ):
            child_category = relationship["child_team_tag"]
            parent_category = relationship["parent_team_tag"]
            # Skip if either parent or child is archived
            if parent_category not in relationships:
                relationships[parent_category] = set()
            relationships[parent_category].add(child_category)
            known_children[child_category] = child_category
            if parent_category not in known_children:
                root_categories[parent_category] = parent_category
            if child_category in root_categories:
                del root_categories[child_category]

        mapped_records: list[dict[str, str | int]] = []
        id_index: dict[str, int] = {}
        # now we can work our way down the tree, starting at the root categories

        nested_tree = self._build_nested_tree(relationships, root_categories)

        def traverse_all_paths(node, ancestors):
            mapped = []
            node_name = node["name"]
            # For every ancestor path, emit a record for each ancestor-child pair
            for idx, ancestor in enumerate(ancestors):
                if (
                    not self.all_teams().get(node_name)
                    # or self.all_teams().get(node_name, {}).get("is_archived")
                    # or self.all_teams().get(ancestor, {}).get("is_archived")
                ):
                    continue
                mapped.append(
                    {
                        "id": str(uuid.uuid4()),
                        "parent_team_tag": ancestor,
                        "child_team_tag": node_name,
                        "is_parent": 1 if idx == len(ancestors) - 1 and len(ancestors) > 0 else 0,
                        "level": idx + 1,
                    }
                )
            # Recurse for each child, passing a *copy* of ancestors + this node
            for child in node.get("children", []):
                mapped.extend(traverse_all_paths(child, ancestors + [node_name]))
            return mapped

        for root in nested_tree.values():
            mapped_records.extend(traverse_all_paths(root, []))
        # now build our id index
        id_index = {str(record["id"]): index for (index, record) in enumerate(mapped_records)}

        return (mapped_records, id_index)

    def _build_nested_tree(self, relationships: dict[str, set[str]], root_categories: dict[str, str]) -> dict:
        def build_subtree(node):
            return {"name": node, "children": [build_subtree(child) for child in relationships.get(node, [])]}

        return {root: build_subtree(root) for root in root_categories}

    def _get_cortex_backend(self) -> rest_backend.CortexBackend:
        """Return the cortex backend."""
        if self.cortex_backend is not None:
            self.di.inject_properties(self.cortex_backend.__class__)
        else:
            self.cortex_backend = self.di.build_class(rest_backend.CortexBackend)
        return self.cortex_backend

    def all_teams(self) -> dict[str, dict[str, Any]]:
        """Return all teams from cortex."""
        if hasattr(self, "_cached_teams"):
            return self._cached_teams

        from clearskies_cortex.models.cortex_team import CortexTeam

        teams: dict[str, dict[str, Any]] = {}
        for team in (
            self._get_cortex_backend()
            .records(
                Query(
                    model_class=CortexTeam,
                    conditions=[Condition("include_teams_without_members=true")],
                ),
            )
            .records
        ):
            teams[team["team_tag"]] = team
        self._cached_teams = teams
        return teams
