#!/usr/bin/env python3
"""
Decomposes the large OpenAPI spec into manageable chunks for LLM processing.

This script splits the Cortex API specification into smaller,
domain-specific chunks that can be processed within LLM context windows.

Usage:
    python tools/spec_decomposer.py [--spec PATH] [--output DIR]

Example:
    python tools/spec_decomposer.py --spec docs/swagger.json --output api_spec/decomposed
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

# Common schemas that are shared across multiple domains
COMMON_SCHEMA_NAMES = {
    # Error handling
    "Error",
    "ErrorDocument",
    "ErrorLink",
    "ErrorSource",
    # JSON:API structures
    "JsonApi",
    "Links",
    "LinkProperty",
    "Meta",
    "PaginatedLinks",
    # Versioning
    "QueryVersion",
    "ActualVersion",
    # Common types
    "Uuid",
    "DateTime",
    # Relationships
    "RelationshipData",
    "RelationshipLinks",
}


def load_spec(spec_path: str | Path) -> dict[str, Any]:
    """Load the OpenAPI specification from a JSON file."""
    with open(spec_path) as f:
        return json.load(f)


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Save data to a JSON file, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def find_schema_refs(obj: Any) -> set[str]:
    """
    Recursively find all schema references ($ref) in an object.

    Returns a set of schema names (without the full path).
    """
    schemas: set[str] = set()

    if isinstance(obj, dict):
        if "$ref" in obj:
            ref = obj["$ref"]
            if ref.startswith("#/components/schemas/"):
                schemas.add(ref.split("/")[-1])
        for value in obj.values():
            schemas.update(find_schema_refs(value))
    elif isinstance(obj, list):
        for item in obj:
            schemas.update(find_schema_refs(item))

    return schemas


def resolve_schema_dependencies(spec: dict[str, Any], schema_names: set[str], max_depth: int = 5) -> set[str]:
    """
    Resolve all schema dependencies recursively.

    Given a set of schema names, find all schemas they reference.
    """
    all_schemas = set(schema_names)
    schemas_to_check = set(schema_names)

    for _ in range(max_depth):
        new_schemas: set[str] = set()
        for schema_name in schemas_to_check:
            schema = spec.get("components", {}).get("schemas", {}).get(schema_name, {})
            refs = find_schema_refs(schema)
            new_schemas.update(refs - all_schemas)

        if not new_schemas:
            break

        all_schemas.update(new_schemas)
        schemas_to_check = new_schemas

    return all_schemas


def extract_common_schemas(spec: dict[str, Any]) -> dict[str, Any]:
    """Extract common schemas that are shared across domains."""
    all_schemas = spec.get("components", {}).get("schemas", {})
    common = {}

    for name in COMMON_SCHEMA_NAMES:
        if name in all_schemas:
            common[name] = all_schemas[name]

    return common


def group_endpoints_by_tag(spec: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Group all endpoints by their tags."""
    endpoints_by_tag: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if not isinstance(details, dict):
                continue

            tags = details.get("tags", ["Untagged"])
            for tag in tags:
                endpoints_by_tag[tag].append(
                    {
                        "path": path,
                        "method": method.upper(),
                        "operation_id": details.get("operationId", ""),
                        "summary": details.get("summary", ""),
                        "details": details,
                    }
                )

    return dict(endpoints_by_tag)


def create_domain_chunk(
    spec: dict[str, Any], tag: str, endpoints: list[dict[str, Any]], common_schema_names: set[str]
) -> dict[str, Any]:
    """Create a domain chunk containing endpoints and their schemas."""
    # Find all schemas referenced by these endpoints
    domain_schemas: set[str] = set()
    for endpoint in endpoints:
        domain_schemas.update(find_schema_refs(endpoint["details"]))

    # Resolve dependencies
    all_domain_schemas = resolve_schema_dependencies(spec, domain_schemas)

    # Remove common schemas (they're in a separate file)
    domain_specific_schemas = all_domain_schemas - common_schema_names

    # Get the actual schema definitions
    all_schemas = spec.get("components", {}).get("schemas", {})
    schemas = {name: all_schemas[name] for name in domain_specific_schemas if name in all_schemas}

    # Create simplified endpoint list (without full details for summary)
    endpoint_summary = [
        {
            "method": ep["method"],
            "path": ep["path"],
            "operation_id": ep["operation_id"],
            "summary": ep["summary"],
        }
        for ep in endpoints
    ]

    return {
        "tag": tag,
        "endpoint_count": len(endpoints),
        "schema_count": len(schemas),
        "endpoints_summary": endpoint_summary,
        "endpoints": endpoints,
        "schemas": schemas,
        "referenced_common_schemas": list(all_domain_schemas & common_schema_names),
    }


def estimate_tokens(data: dict[str, Any]) -> int:
    """Estimate the number of tokens in a JSON object (rough approximation)."""
    json_str = json.dumps(data)
    # Rough estimate: 4 characters per token
    return len(json_str) // 4


def decompose_spec(spec_path: str | Path, output_dir: str | Path, max_tokens_per_chunk: int = 15000) -> dict[str, Any]:
    """
    Decompose the OpenAPI spec into domain chunks.

    Args:
        spec_path: Path to the OpenAPI spec JSON file
        output_dir: Directory to write the chunks
        max_tokens_per_chunk: Maximum estimated tokens per chunk

    Returns:
        Manifest dictionary with metadata about all chunks
    """
    spec = load_spec(spec_path)
    output_dir = Path(output_dir)

    # Extract common schemas
    common_schemas = extract_common_schemas(spec)
    common_schema_names = set(common_schemas.keys())

    # Save common schemas
    save_json(
        output_dir / "shared" / "common_schemas.json",
        {
            "description": "Common schemas shared across all domains",
            "schemas": common_schemas,
        },
    )

    # Extract common parameters
    common_params = spec.get("components", {}).get("parameters", {})
    save_json(
        output_dir / "shared" / "common_parameters.json",
        {
            "description": "Common parameters shared across endpoints",
            "parameters": common_params,
        },
    )

    # Group endpoints by tag
    endpoints_by_tag = group_endpoints_by_tag(spec)

    # Create manifest
    manifest: dict[str, Any] = {
        "spec_info": spec.get("info", {}),
        "total_endpoints": sum(len(eps) for eps in endpoints_by_tag.values()),
        "total_tags": len(endpoints_by_tag),
        "shared_files": [
            "shared/common_schemas.json",
            "shared/common_parameters.json",
        ],
        "chunks": [],
    }

    # Create domain chunks
    for tag, endpoints in sorted(endpoints_by_tag.items(), key=lambda x: -len(x[1])):
        tag_slug = tag.lower().replace(" ", "_").replace("-", "_")

        chunk = create_domain_chunk(spec, tag, endpoints, common_schema_names)
        estimated_tokens = estimate_tokens(chunk)

        chunk_meta = {
            "tag": tag,
            "slug": tag_slug,
            "path": f"chunks/domain_{tag_slug}.json",
            "endpoint_count": len(endpoints),
            "schema_count": chunk["schema_count"],
            "estimated_tokens": estimated_tokens,
            "needs_splitting": estimated_tokens > max_tokens_per_chunk,
        }

        # If chunk is too large, split by endpoint
        if estimated_tokens > max_tokens_per_chunk and len(endpoints) > 3:
            # Split into smaller chunks
            sub_chunks = split_large_domain(spec, tag, endpoints, common_schema_names, max_tokens_per_chunk)

            for i, sub_chunk in enumerate(sub_chunks):
                sub_path = f"chunks/domain_{tag_slug}_part{i + 1}.json"
                save_json(output_dir / sub_path, sub_chunk)

                manifest["chunks"].append(
                    {
                        "tag": tag,
                        "slug": f"{tag_slug}_part{i + 1}",
                        "path": sub_path,
                        "endpoint_count": sub_chunk["endpoint_count"],
                        "schema_count": sub_chunk["schema_count"],
                        "estimated_tokens": estimate_tokens(sub_chunk),
                        "is_partial": True,
                        "part": i + 1,
                        "total_parts": len(sub_chunks),
                    }
                )
        else:
            save_json(output_dir / chunk_meta["path"], chunk)
            manifest["chunks"].append(chunk_meta)

    # Save manifest
    save_json(output_dir / "manifest.json", manifest)

    return manifest


def split_large_domain(
    spec: dict[str, Any], tag: str, endpoints: list[dict[str, Any]], common_schema_names: set[str], max_tokens: int
) -> list[dict[str, Any]]:
    """Split a large domain into smaller chunks."""
    chunks: list[dict[str, Any]] = []
    current_endpoints: list[dict[str, Any]] = []

    for endpoint in endpoints:
        current_endpoints.append(endpoint)

        # Create a test chunk to estimate size
        test_chunk = create_domain_chunk(spec, tag, current_endpoints, common_schema_names)

        if estimate_tokens(test_chunk) > max_tokens and len(current_endpoints) > 1:
            # Remove last endpoint and save chunk
            current_endpoints.pop()
            chunk = create_domain_chunk(spec, tag, current_endpoints, common_schema_names)
            chunks.append(chunk)
            current_endpoints = [endpoint]

    # Add remaining endpoints
    if current_endpoints:
        chunk = create_domain_chunk(spec, tag, current_endpoints, common_schema_names)
        chunks.append(chunk)

    return chunks


def print_summary(manifest: dict[str, Any]) -> None:
    """Print a summary of the decomposition."""
    print("\n" + "=" * 60)
    print("SPEC DECOMPOSITION SUMMARY")
    print("=" * 60)
    print(f"\nTotal Endpoints: {manifest['total_endpoints']}")
    print(f"Total Tags: {manifest['total_tags']}")
    print(f"Total Chunks: {len(manifest['chunks'])}")

    print("\n" + "-" * 60)
    print("CHUNKS BY SIZE (estimated tokens)")
    print("-" * 60)

    for chunk in sorted(manifest["chunks"], key=lambda x: -x["estimated_tokens"]):
        status = "⚠️ LARGE" if chunk.get("needs_splitting") else "✅"
        partial = f" (part {chunk['part']}/{chunk['total_parts']})" if chunk.get("is_partial") else ""
        print(
            f"{status} {chunk['tag']}{partial}: "
            f"{chunk['endpoint_count']} endpoints, "
            f"{chunk['schema_count']} schemas, "
            f"~{chunk['estimated_tokens']} tokens"
        )

    print("\n" + "=" * 60)


def main() -> None:
    """Run the spec decomposer."""
    parser = argparse.ArgumentParser(description="Decompose OpenAPI spec into LLM-friendly chunks")
    parser.add_argument(
        "--spec",
        default="docs/swagger.json",
        help="Path to the OpenAPI spec JSON file",
    )
    parser.add_argument(
        "--output",
        default="api_spec/decomposed",
        help="Output directory for chunks",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=15000,
        help="Maximum estimated tokens per chunk",
    )

    args = parser.parse_args()

    print(f"Loading spec from: {args.spec}")
    print(f"Output directory: {args.output}")

    manifest = decompose_spec(args.spec, args.output, args.max_tokens)

    print_summary(manifest)

    print(f"\n✅ Decomposition complete!")
    print(f"   Manifest: {args.output}/manifest.json")


if __name__ == "__main__":
    main()
