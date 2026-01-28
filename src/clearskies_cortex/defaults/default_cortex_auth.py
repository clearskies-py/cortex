import clearskies


class DefaultCortexAuth(clearskies.di.AdditionalConfigAutoImport):
    """
    Default authentication provider for Cortex API.

    This class provides automatic configuration for Cortex API authentication using
    the clearskies dependency injection system. It is auto-imported when the clearskies_cortex
    package is used, making authentication configuration seamless.

    The authentication can be configured in two ways:

    1. **Secret Path (recommended for production)**: Set the `CORTEX_AUTH_SECRET_PATH` environment
       variable to point to a secret manager path containing the API key.

    2. **Direct Environment Key**: Set the `CORTEX_AUTH_KEY` environment variable directly
       with the Cortex API key.

    ```python
    import clearskies
    from clearskies_cortex.models import CortexTeam

    # The authentication is automatically configured via environment variables
    # Option 1: Using secret path
    # export CORTEX_AUTH_SECRET_PATH=/path/to/secret

    # Option 2: Using direct key
    # export CORTEX_AUTH_KEY=your-api-key

    # Then use models normally - auth is handled automatically
    teams = CortexTeam()
    for team in teams:
        print(team.get_name())
    ```
    """

    def provide_cortex_auth(self, environment: clearskies.Environment):
        """
        Provide the Cortex authentication configuration.

        Checks for `CORTEX_AUTH_SECRET_PATH` first, falling back to `CORTEX_AUTH_KEY`
        if not set. Returns a SecretBearer authentication instance configured for
        the Cortex API.

        Args:
            environment: The clearskies Environment instance for accessing env variables.

        Returns:
            A SecretBearer authentication instance configured for Cortex API.
        """
        if environment.get("CORTEX_AUTH_SECRET_PATH", True):
            secret_key = environment.get("CORTEX_AUTH_SECRET_PATH")
            return clearskies.authentication.SecretBearer(secret_key=secret_key, header_prefix="Bearer ")
        return clearskies.authentication.SecretBearer(environment_key="CORTEX_AUTH_KEY", header_prefix="Bearer ")
