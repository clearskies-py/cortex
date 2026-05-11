"""
Shared schema definitions and helpers for testing.

This module provides utilities for creating Cortex API compliant responses
that match the Cortex REST API format.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _generate_entity_id() -> str:
    """Generate a Cortex entity ID (18-character format)."""
    # Cortex uses 'en' prefix followed by 16 hex characters
    return f"en{uuid4().hex[:16]}"


def _timestamp() -> str:
    """Generate an ISO 8601 timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def make_pagination_info(
    page: int = 0,
    total: int = 1,
    total_pages: int = 1,
) -> dict[str, int]:
    """
    Create pagination information for a response.

    Args:
        page: Current page number (0-indexed)
        total: Total number of results
        total_pages: Total number of pages

    Returns:
        A dictionary with pagination fields
    """
    return {
        "page": page,
        "total": total,
        "totalPages": total_pages,
    }


def make_cortex_response(
    data: list[dict[str, Any]] | dict[str, Any],
    data_key: str = "entities",
    page: int = 0,
    total: int | None = None,
    total_pages: int | None = None,
) -> dict[str, Any]:
    """
    Create a Cortex API compliant response.

    Args:
        data: The primary data (single resource or list of resources)
        data_key: The key name for the data in the response (e.g., "entities", "teams", "scorecards")
        page: Current page number (0-indexed)
        total: Total number of results (defaults to length of data if list)
        total_pages: Total number of pages (defaults to 1)

    Returns:
        A dictionary in Cortex API format
    """
    if isinstance(data, list):
        actual_total = total if total is not None else len(data)
        actual_total_pages = total_pages if total_pages is not None else 1
    else:
        actual_total = total if total is not None else 1
        actual_total_pages = total_pages if total_pages is not None else 1

    response: dict[str, Any] = {
        data_key: data,
        "page": page,
        "total": actual_total,
        "totalPages": actual_total_pages,
    }
    return response


def make_entity_resource(
    tag: str,
    name: str,
    entity_type: str = "service",
    id: str | None = None,
    description: str | None = None,
    groups: list[str] | None = None,
    is_archived: bool = False,
    last_updated: str | None = None,
    git: dict[str, Any] | None = None,
    hierarchy: dict[str, Any] | None = None,
    links: list[dict[str, Any]] | None = None,
    metadata: list[dict[str, Any]] | None = None,
    owners: dict[str, Any] | None = None,
    ownership: dict[str, Any] | None = None,
    slack_channels: list[dict[str, Any]] | None = None,
    members: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Create a Cortex catalog entity resource object.

    Args:
        tag: The unique entity tag (x-cortex-tag)
        name: Human-readable name for the entity
        entity_type: Type of entity (service, domain, team, etc.)
        id: Unique auto-generated identifier (auto-generated if not provided)
        description: Entity description
        groups: List of groups the entity belongs to
        is_archived: Whether the entity is archived
        last_updated: Last updated timestamp
        git: Git repository information
        hierarchy: Parent/child hierarchy information
        links: External links
        metadata: Custom metadata key/values
        owners: Owner information (v2 format)
        ownership: Ownership configuration
        slack_channels: Slack channel configurations
        members: Team member information (for team entities)

    Returns:
        A dictionary representing a Cortex entity
    """
    resource: dict[str, Any] = {
        "id": id or _generate_entity_id(),
        "tag": tag,
        "name": name,
        "type": entity_type,
        "groups": groups or [],
        "isArchived": is_archived,
        "lastUpdated": last_updated or _timestamp(),
        "links": links or [],
        "slackChannels": slack_channels or [],
    }

    if description is not None:
        resource["description"] = description

    if git is not None:
        resource["git"] = git

    if hierarchy is not None:
        resource["hierarchy"] = hierarchy
    else:
        resource["hierarchy"] = {"parents": [], "children": []}

    if metadata is not None:
        resource["metadata"] = metadata

    if owners is not None:
        resource["owners"] = owners

    if ownership is not None:
        resource["ownership"] = ownership

    if members is not None:
        resource["members"] = members

    return resource


def make_hierarchy_node(
    tag: str,
    name: str,
    node_type: str = "domain",
    id: str | None = None,
    description: str | None = None,
    groups: list[str] | None = None,
    definition: dict[str, Any] | None = None,
    parents: list[dict[str, Any]] | None = None,
    children: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Create a hierarchy node for parent/child relationships.

    Args:
        tag: Entity tag
        name: Entity name
        node_type: Entity type
        id: Entity ID
        description: Entity description
        groups: Entity groups
        definition: Entity definition
        parents: Parent nodes (for parent hierarchy)
        children: Child nodes (for child hierarchy)

    Returns:
        A dictionary representing a hierarchy node
    """
    node: dict[str, Any] = {
        "id": id or _generate_entity_id(),
        "tag": tag,
        "name": name,
        "type": node_type,
    }

    if description is not None:
        node["description"] = description

    if groups is not None:
        node["groups"] = groups

    if definition is not None:
        node["definition"] = definition

    # Include parents or children based on what's provided
    if parents is not None:
        node["parents"] = parents
    if children is not None:
        node["children"] = children

    return node


def make_link(
    name: str,
    url: str,
    link_type: str = "documentation",
    description: str | None = None,
) -> dict[str, Any]:
    """
    Create a link object.

    Args:
        name: Human-readable name for the link
        url: The URL
        link_type: Type of link (documentation, runbook, etc.)
        description: Optional description

    Returns:
        A dictionary representing a link
    """
    link: dict[str, Any] = {
        "name": name,
        "url": url,
        "type": link_type,
    }
    if description is not None:
        link["description"] = description
    return link


def make_metadata(
    key: str,
    value: Any,
) -> dict[str, Any]:
    """
    Create a metadata key/value object.

    Args:
        key: The custom data key
        value: The value (can be any JSON-serializable type)

    Returns:
        A dictionary representing metadata
    """
    return {
        "key": key,
        "value": value,
    }


def make_slack_channel(
    name: str,
    notifications_enabled: bool = True,
    description: str | None = None,
) -> dict[str, Any]:
    """
    Create a Slack channel object.

    Args:
        name: Channel name (without #)
        notifications_enabled: Whether notifications are enabled
        description: Optional description

    Returns:
        A dictionary representing a Slack channel
    """
    channel: dict[str, Any] = {
        "name": name,
        "notificationsEnabled": notifications_enabled,
    }
    if description is not None:
        channel["description"] = description
    return channel


def make_owner_details(
    teams: list[dict[str, Any]] | None = None,
    individuals: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Create owner details object (v2 format).

    Args:
        teams: List of team owners
        individuals: List of individual owners

    Returns:
        A dictionary representing owner details
    """
    return {
        "teams": teams or [],
        "individuals": individuals or [],
    }


def make_team_owner(
    tag: str,
    name: str,
    id: str | None = None,
    description: str | None = None,
    is_archived: bool = False,
    provider: str | None = None,
    inheritance: str | None = None,
) -> dict[str, Any]:
    """
    Create a team owner object.

    Args:
        tag: Team tag
        name: Team name
        id: Team ID
        description: Team description
        is_archived: Whether team is archived
        provider: Provider (CORTEX, GITHUB, etc.)
        inheritance: Inheritance type (APPEND, FALLBACK, NONE)

    Returns:
        A dictionary representing a team owner
    """
    owner: dict[str, Any] = {
        "id": id or _generate_entity_id(),
        "tag": tag,
        "name": name,
        "isArchived": is_archived,
    }
    if description is not None:
        owner["description"] = description
    if provider is not None:
        owner["provider"] = provider
    if inheritance is not None:
        owner["inheritance"] = inheritance
    return owner


def make_individual_owner(
    email: str,
    description: str | None = None,
) -> dict[str, Any]:
    """
    Create an individual owner object.

    Args:
        email: Owner email
        description: Optional description

    Returns:
        A dictionary representing an individual owner
    """
    owner: dict[str, Any] = {"email": email}
    if description is not None:
        owner["description"] = description
    return owner


def make_team_member(
    email: str,
    name: str,
    roles: list[dict[str, Any]] | None = None,
    sources: list[dict[str, Any]] | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """
    Create a team member object.

    Args:
        email: Member email
        name: Member name
        roles: List of roles
        sources: List of member sources
        description: Optional description

    Returns:
        A dictionary representing a team member
    """
    member: dict[str, Any] = {
        "email": email,
        "name": name,
        "roles": roles or [],
        "sources": sources or [],
    }
    if description is not None:
        member["description"] = description
    return member


def make_git_details(
    repository: str,
    provider: str = "github",
    repository_url: str | None = None,
    alias: str | None = None,
    basepath: str | None = None,
) -> dict[str, Any]:
    """
    Create Git repository details.

    Args:
        repository: Repository name
        provider: Git provider (github, gitlab, bitbucket, azure-devops)
        repository_url: Full repository URL
        alias: Custom alias for multi-account support
        basepath: Subdirectory for monorepo

    Returns:
        A dictionary representing Git details
    """
    git: dict[str, Any] = {
        "repository": repository,
        "provider": provider,
        "repositoryUrl": repository_url or f"https://{provider}.com/{repository}",
    }
    if alias is not None:
        git["alias"] = alias
    if basepath is not None:
        git["basepath"] = basepath
    return git


def make_error_response(
    message: str,
    error_type: str = "BAD_REQUEST",
    details: str | None = None,
    http_status: int | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    """
    Create a Cortex API error response.

    Args:
        message: Error message
        error_type: Error type enum value
        details: Additional error details
        http_status: HTTP status code
        request_id: Request ID for tracking

    Returns:
        A dictionary representing an error response
    """
    error: dict[str, Any] = {
        "message": message,
        "type": error_type,
    }
    if details is not None:
        error["details"] = details
    if http_status is not None:
        error["httpStatus"] = http_status
    if request_id is not None:
        error["requestId"] = request_id
    return error


# Pre-defined error responses for common cases
ERROR_400 = make_error_response(
    message="Bad Request",
    error_type="BAD_REQUEST",
    http_status=400,
)

ERROR_401 = make_error_response(
    message="Unauthorized",
    error_type="INTEGRATION_UNAUTHORIZED",
    http_status=401,
)

ERROR_403 = make_error_response(
    message="Forbidden",
    error_type="FORBIDDEN",
    http_status=403,
)

ERROR_404 = make_error_response(
    message="Not found",
    error_type="NOT_FOUND",
    http_status=404,
)

ERROR_429 = make_error_response(
    message="Too many requests",
    error_type="INTEGRATION_RATE_LIMITED",
    http_status=429,
)

ERROR_500 = make_error_response(
    message="Internal server error",
    error_type="UNHANDLED_EXCEPTION",
    http_status=500,
)
