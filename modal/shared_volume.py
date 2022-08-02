from modal_proto import api_pb2
from modal_utils.async_utils import synchronize_apis
from modal_utils.grpc_utils import retry_transient_errors

from .object import Object


class _SharedVolume(Object, type_prefix="sv"):
    """A shared, writable file system accessible by one or more Modal functions.

    By attaching this file system as a mount to one or more functions, they can
    share and persist data with each other.

    **Usage**

    ```python
    import modal

    stub = modal.Stub()

    @stub.function(shared_volumes={"/root/foo": modal.SharedVolume()})
    def f():
        pass
    ```

    It is often the case that you would want to persist a shared volume object
    separately from the currently attached app. Refer to the persistence
    [guide section](/docs/guide/shared-volumes#persisting-volumes) to see how to
    persist this object across app runs.
    """

    def __init__(self) -> None:
        """Construct a new shared volume, which is empty by default."""
        super().__init__()

    def _get_creating_message(self) -> str:
        return "Creating shared volume..."

    def _get_created_message(self) -> str:
        return "Created shared volume."

    async def _load(self, client, app_id, existing_shared_volume_id):
        if existing_shared_volume_id:
            # Volume already exists; do nothing.
            return existing_shared_volume_id

        req = api_pb2.SharedVolumeCreateRequest(app_id=app_id)
        resp = await retry_transient_errors(client.stub.SharedVolumeCreate, req)
        return resp.shared_volume_id


SharedVolume, AioSharedVolume = synchronize_apis(_SharedVolume)
