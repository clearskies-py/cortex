from clearskies import Model

from clearskies_cortex.backends import CortexBackend


class CortexModel(Model):
    """
    Base model for Cortex API integration.

    This is the foundational model class for all Cortex-related models. It pre-configures
    the CortexBackend for API communication with the Cortex platform.

    Extend this class to create models that interact with the Cortex API:

    ```python
    from clearskies_cortex.models import CortexModel
    from clearskies.columns import String, Json


    class MyCustomCortexModel(CortexModel):
        id_column_name = "my_id"

        my_id = String()
        data = Json()

        @classmethod
        def destination_name(cls):
            return "my-endpoint"
    ```
    """

    backend = CortexBackend()
