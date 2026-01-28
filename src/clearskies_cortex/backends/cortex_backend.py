from typing import Any

import clearskies
import requests
from clearskies import configs
from clearskies.authentication import Authentication
from clearskies.decorators import parameters_to_properties
from clearskies.di import inject
from clearskies.query import Query


class CortexBackend(clearskies.backends.ApiBackend):
    """
    Backend for interacting with the Cortex.io API.

    This backend extends the ApiBackend to provide seamless integration with the Cortex.io platform.
    It handles the specific pagination and response format used by Cortex APIs, where pagination
    information (`page`, `totalPages`, `total`) is returned in the response body rather than headers.

    ## Usage

    The CortexBackend is typically used with models that represent Cortex entities:

    ```python
    import clearskies
    from clearskies_cortex.backends import CortexBackend


    class CortexService(clearskies.Model):
        backend = CortexBackend()

        @classmethod
        def destination_name(cls) -> str:
            return "catalog/services"

        tag = clearskies.columns.String()
        name = clearskies.columns.String()
        description = clearskies.columns.String()
    ```

    ## Authentication

    By default, the backend uses the `cortex_auth` binding for authentication, which should be
    configured in your application's dependency injection container. You can also provide a custom
    authentication instance:

    ```python
    backend = CortexBackend(
        authentication=clearskies.authentication.SecretBearer(
            environment_key="CORTEX_API_KEY",
        )
    )
    ```

    ## Pagination

    The Cortex API uses page-based pagination with the following response format:

    ```json
    {
        "entities": [...],
        "page": 1,
        "totalPages": 5,
        "total": 100
    }
    ```

    The backend automatically handles extracting pagination data and provides the next page
    information to clearskies for seamless iteration through results.
    """

    """
    The base URL for the Cortex API.
    """
    base_url = configs.String(default="https://api.getcortexapp.com/api/v1/")

    """
    The authentication instance to use for API requests.

    By default, this uses the `cortex_auth` binding from the dependency injection container.
    """
    authentication = inject.ByName("cortex_auth")  # type: ignore[assignment]

    """
    The requests instance for making HTTP calls.
    """
    requests = inject.Requests()

    """
    The casing style used by the Cortex API (camelCase by default).
    """
    api_casing = configs.Select(["snake_case", "camelCase", "TitleCase"], default="camelCase")

    _auth_headers: dict[str, str] = {}

    """
    A mapping from API response keys to model column names.
    """
    api_to_model_map = configs.AnyDict(default={})

    """
    The name of the pagination parameter used in requests.
    """
    pagination_parameter_name = configs.String(default="page")

    """
    The name of the limit parameter used in requests.
    """
    limit_parameter_name = configs.String(default="pageSize")

    can_count = False

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

    def map_records_response(
        self, response_data: Any, query: Query, query_data: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Map the Cortex API response to model fields.

        The Cortex API returns responses in a specific format where the actual records are nested
        within a dictionary alongside pagination metadata. This method extracts the records and
        removes the pagination fields before passing to the parent implementation.

        Example Cortex API response:

        ```json
        {
            "entities": [{"tag": "service-1", "name": "My Service"}, ...],
            "page": 1,
            "totalPages": 5,
            "total": 100
        }
        ```

        This method will extract the `entities` list and pass it to the parent for further processing.
        """
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

    def get_next_page_data_from_response(
        self,
        query: Query,
        response: "requests.Response",  # type: ignore
    ) -> dict[str, Any]:
        """
        Extract pagination data from the Cortex API response.

        The Cortex API includes pagination information in the response body:

        - `page`: The current page number
        - `totalPages`: The total number of pages available
        - `total`: The total number of records

        This method checks if there are more pages available and returns the next page number
        if so. It also extracts total count information for use in RecordsQueryResult.
        The returned dictionary is used by clearskies to fetch subsequent pages and
        populate count metadata.

        Returns:
            A dictionary containing:
            - The next page number if more pages exist
            - total_count: The total number of records (if available)
            - total_pages: The total number of pages (if available)
        """
        next_page_data: dict[str, Any] = {}

        response_data = response.json() if response.content else {}

        if isinstance(response_data, dict):
            # Extract count information from response body
            count_info = self.extract_count_from_response(None, response_data)
            if count_info:
                total_count, total_pages = count_info
                if total_count is not None:
                    next_page_data["total_count"] = total_count
                if total_pages is not None:
                    next_page_data["total_pages"] = total_pages

            # Check if there are more pages
            page = response_data.get("page", None)
            total_pages_from_response = response_data.get("totalPages", None)
            if page is not None and total_pages_from_response is not None and page < total_pages_from_response:
                next_page_data[self.pagination_parameter_name] = page + 1

        return next_page_data

    def extract_count_from_response(
        self,
        response_headers: dict[str, str] | None = None,
        response_data: Any = None,
    ) -> tuple[int | None, int | None]:
        """
        Extract count information from the Cortex API response body.

        Unlike many APIs that return count information in headers, the Cortex API includes
        this data in the response body:

        - `total`: The total number of records matching the query
        - `totalPages`: The total number of pages available

        This method extracts these values and returns them as a tuple for use in
        `RecordsQueryResult`.

        Returns:
            A tuple of (total_count, total_pages) where either value may be None
            if not present in the response.
        """
        if not isinstance(response_data, dict):
            return (None, None)

        total_count = response_data.get("total", None)
        total_pages = response_data.get("totalPages", None)

        return (total_count, total_pages)
