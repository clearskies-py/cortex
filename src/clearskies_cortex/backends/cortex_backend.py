from typing import Any

import clearskies
from clearskies import Column, configs
from clearskies.authentication import Authentication
from clearskies.decorators import parameters_to_properties
from clearskies.di import inject
from clearskies.query import Query


class CortexBackend(clearskies.backends.ApiBackend):
    """Backend for Cortex.io."""

    base_url = configs.String(default="https://api.getcortexapp.com/api/v1/")
    authentication = inject.ByName("cortex_auth")  # type: ignore[assignment]
    requests = inject.Requests()
    api_casing = configs.Select(["snake_case", "camelCase", "TitleCase"], default="camelCase")

    _auth_headers: dict[str, str] = {}

    api_to_model_map = configs.AnyDict(default={})
    pagination_parameter_name = configs.String(default="page")

    can_count = True

    @parameters_to_properties
    def __init__(
        self,
        base_url: str | None = "https://api.getcortexapp.com/api/v1/",
        authentication: Authentication | None = None,
        model_casing: str = "snake_case",
        api_casing: str = "camelCase",
        api_to_model_map: dict[str, str | list[str]] = {},
        pagination_parameter_name: str = "page",
        pagination_parameter_type: str = "int",
        limit_parameter_name: str = "pageSize",
    ):
        self.finalize_and_validate_configuration()

    def count(self, query: Query) -> int:
        """Return count of records matching query."""
        self.check_query(query)
        (url, method, body, headers) = self.build_records_request(query)
        response = self.execute_request(url, method, json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "total" in data:
            return data["total"]
        data = self.map_records_response(data, query)
        return len(data)

    def map_records_response(
        self, response_data: Any, query: Query, query_data: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Map api response to model fields."""
        if isinstance(response_data, dict):
            if "page" in response_data:
                del response_data["page"]
                del response_data["totalPages"]
                del response_data["total"]
            first_item = next(iter(response_data))
            if isinstance(response_data[first_item], list) and all(
                isinstance(item, dict) for item in response_data[first_item]
            ):
                return super().map_records_response(response_data[first_item], query, query_data)
        return super().map_records_response(response_data, query, query_data)
