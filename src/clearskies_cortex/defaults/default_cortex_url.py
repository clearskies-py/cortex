import clearskies


class DefaultCortexUrl(clearskies.di.AdditionalConfigAutoImport):
    """
    Default URL provider for Cortex API.

    This class provides automatic configuration for the Cortex API base URL using
    the clearskies dependency injection system. It is auto-imported when the clearskies_cortex
    package is used, making URL configuration seamless.

    The URL can be configured via the `CORTEX_URL` environment variable. If not set,
    it defaults to the standard Cortex API endpoint: `https://api.getcortexapp.com/api/v1/`

    ```python
    import clearskies
    from clearskies_cortex.models import CortexTeam

    # The URL is automatically configured via environment variable
    # export CORTEX_URL=https://custom-cortex-instance.example.com/api/v1/

    # Or use the default Cortex API URL by not setting the variable

    # Then use models normally - URL is handled automatically
    teams = CortexTeam()
    for team in teams:
        print(team.get_name())
    ```
    """

    def provide_cortex_url(self, environment: clearskies.Environment) -> str:
        """
        Provide the Cortex API base URL.

        Checks for `CORTEX_URL` environment variable, falling back to the default
        Cortex API URL if not set.

        Args:
            environment: The clearskies Environment instance for accessing env variables.

        Returns:
            The Cortex API base URL string.
        """
        cortex_url = environment.get("CORTEX_URL", True)
        return cortex_url if cortex_url else "https://api.getcortexapp.com/api/v1/"
