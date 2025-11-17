import clearskies


class DefaultCortexUrl(clearskies.di.AdditionalConfigAutoImport):
    def provide_cortex_url(self, environment: clearskies.Environment) -> str:
        cortex_url = environment.get("CORTEX_URL", True)
        return cortex_url if cortex_url else "https://api.getcortexapp.com/api/v1/"
