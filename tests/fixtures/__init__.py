"""
Test fixtures package for clearskies_cortex.

This package provides factory functions and helpers for creating mock API responses
that match the Cortex REST API format.
"""

from tests.fixtures.api_responses import (
    CatalogEntityResponseFactory,
    ScorecardResponseFactory,
    TeamResponseFactory,
)
from tests.fixtures.schemas import (
    make_cortex_response,
    make_entity_resource,
    make_error_response,
    make_hierarchy_node,
    make_link,
    make_metadata,
    make_owner_details,
    make_pagination_info,
    make_slack_channel,
    make_team_member,
)

__all__ = [
    # Response factories
    "CatalogEntityResponseFactory",
    "ScorecardResponseFactory",
    "TeamResponseFactory",
    # Schema helpers
    "make_cortex_response",
    "make_entity_resource",
    "make_error_response",
    "make_hierarchy_node",
    "make_link",
    "make_metadata",
    "make_owner_details",
    "make_pagination_info",
    "make_slack_channel",
    "make_team_member",
]
