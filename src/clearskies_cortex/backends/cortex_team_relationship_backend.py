import logging
import uuid
from types import SimpleNamespace
from typing import Any

from clearskies import Model
from clearskies.backends.memory_backend import MemoryBackend, MemoryTable
from clearskies.columns import String, Uuid
from clearskies.di import inject
from clearskies.query.query import Query

from clearskies_cortex.backends import cortex_backend


class CortexTeamRelationshipBackend(MemoryBackend):
    """Backend for Cortex.io."""

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        cortex_backend,
        silent_on_missing_tables=True,
    ):
        super().__init__(silent_on_missing_tables)
        if cortex_backend is not None:
            self.cortex_backend = cortex_backend

    def records(self, query: Query, next_page_data: dict[str, str | int] | None = None) -> list[dict[str, Any]]:
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

        return super().records(query, next_page_data)

    def _fetch_and_map_relationship_data(self, table_name: str) -> tuple[list[dict[str, str | int]], dict[str, int]]:
        class RelationshipModel(Model):
            id_column_name: str = "id"
            backend = cortex_backend.CortexBackend()

            id = Uuid()
            child_team_tag = String()
            parent_team_tag = String()
            provider = String()

            @classmethod
            def destination_name(cls) -> str:
                return "teams/relationships"

        relationship_data = self.cortex_backend.records(
            Query(
                model_class=RelationshipModel,
            ),
            {},
        )
        # this should match up to exactly what backend.records() will return
        # relationship_data = example_data["edges"]

        # we need to map this to the kind of row structure expected by the category_tree column
        # (see https://github.com/clearskies-py/clearskies/blob/main/src/clearskies/columns/category_tree.py)
        # This takes slightly more time up front but makes for quick lookups in both directions (and we'll
        # cache the result so it only has to happen once).  The trouble is that we need to know the tree before
        # we can get started.  We want to start at the top or the bottom, but Cortex gives us neither.
        # therefore, we'll search for the root categories and then start over.  While we find those, we'll
        # convert from a list of edges to a dictionary of parent/children
        root_categories: dict[str, str] = {}
        known_children: dict[str, str] = {}
        relationships: dict[str, list[str]] = {}
        for relationship in relationship_data:
            child_category = relationship.get("child_team_tag", "")
            parent_category = relationship.get("parent_team_tag", "")
            if parent_category not in relationships:
                relationships[parent_category] = []
            relationships[parent_category].append(child_category)
            known_children[child_category] = child_category
            if parent_category not in known_children:
                root_categories[parent_category] = parent_category
            if child_category in root_categories:
                del root_categories[child_category]

        mapped_records: list[dict[str, str | int]] = []
        id_index: dict[str, int] = {}

        # now we can work our way down the tree, starting at the root categories
        for root in root_categories:
            mapped_records.extend(self._build_mapping_records(root, relationships, []))

        # now build our id index
        id_index = {str(record["id"]): index for (index, record) in enumerate(mapped_records)}

        return (mapped_records, id_index)

    def _build_mapping_records(
        self, category: str, relationships: dict[str, list[str]], parents: list[str]
    ) -> list[dict[str, str | int]]:
        mapped_records: list[dict[str, str | int]] = []
        for level, parent in enumerate(parents):
            mapped_records.append(
                {
                    "id": str(uuid.uuid4()),
                    "parentTeamTag": parent,
                    "childTeamTag": category,
                    "isParent": 1 if level + 1 == len(parents) else 0,
                    "level": level,
                }
            )

        for child in relationships.get(category, []):
            mapped_records.extend(
                self._build_mapping_records(
                    child,
                    relationships,
                    [*parents, category],
                )
            )
        return mapped_records
