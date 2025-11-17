import clearskies


class DefaultCortexAuth(clearskies.di.AdditionalConfigAutoImport):
    def provide_cortex_auth(self, environment: clearskies.Environment):
        if environment.get("CORTEX_AUTH_SECRET_PATH", True):
            secret_key = environment.get("CORTEX_AUTH_SECRET_PATH")
            return clearskies.authentication.SecretBearer(secret_key=secret_key, header_prefix="Bearer ")
        return clearskies.authentication.SecretBearer(environment_key="CORTEX_AUTH_KEY", header_prefix="Bearer ")
