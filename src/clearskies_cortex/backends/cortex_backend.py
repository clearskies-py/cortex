from typing import Any

import clearskies
import requests
from clearskies import Column, configs
from clearskies.authentication import Authentication
from clearskies.decorators import parameters_to_properties
from clearskies.di import inject
from clearskies.query import Query
from clearskies.query.result import CountQueryResult


class CortexBackend(clearskies.backends.ApiBackend):
    """Backend for Cortex.io."""

    base_url = configs.String(default="https://api.getcortexapp.com/api/v1/")
    authentication = inject.ByName("cortex_auth")  # type: ignore[assignment]
    requests = inject.Requests()
    api_casing = configs.Select(["snake_case", "camelCase", "TitleCase"], default="camelCase")

    _auth_headers: dict[str, str] = {}

    api_to_model_map = configs.AnyDict(default={})
    pagination_parameter_name = configs.String(default="page")
    limit_parameter_name = configs.String(default="pageSize")

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

    def count(self, query: Query) -> CountQueryResult:
        """Return count of records matching query."""
        self.check_query(query)
        (url, method, body, headers) = self.build_records_request(query)
        response = self.execute_request(url, method, json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "total" in data:
            return CountQueryResult(count=data["total"])
        data = self.map_records_response(data, query)
        return CountQueryResult(count=len(data))

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

    def set_next_page_data_from_response(
        self,
        next_page_data: dict[str, Any],
        query: Query,
        response: "requests.Response",  # type: ignore
    ) -> None:
        """
        Update the next_page_data dictionary with the appropriate data needed to fetch the next page of records.

        This method has a very important job, which is to inform clearskies about how to make another API call to fetch the next
        page of records.  The way this happens is by updating the `next_page_data` dictionary in place with whatever pagination
        information is necessary.  Note that this relies on next_page_data being passed by reference, hence the need to update
        it in place.  That means that you can do this:

        ```python
        next_page_data["some_key"] = "some_value"
        ```

        but if you do this:

        ```python
        next_page_data = {"some_key": "some_value"}
        ```

        Then things simply won't work.
        """
        if isinstance(response.json(), dict):
            page = response.json().get("page", None)
            total_pages = response.json().get("totalPages", None)
            if page is not None and total_pages is not None and page < total_pages:
                next_page_data[self.pagination_parameter_name] = page + 1
