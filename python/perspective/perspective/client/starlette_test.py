################################################################################
#
# Copyright (c) 2022, the Perspective Authors.
#
# This file is part of the Perspective library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#

from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from .websocket import (
    PerspectiveWebsocketClient,
    PerspectiveWebsocketConnection,
    Periodic,
)


class _StarletteTestPeriodic(Periodic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dont do anything as this should only ever be used in tests

    async def start(self):
        # Dont do anything as this should only ever be used in tests
        ...

    async def stop(self):
        # Dont do anything as this should only ever be used in tests
        ...


class _PerspectiveStarletteWebsocketConnection(PerspectiveWebsocketConnection):
    def __init__(self, client: TestClient):
        self._client = client
        self._ws = None
        self._on_message = None

    async def connect(self, url, on_message, max_message_size) -> None:
        self._ws = self._client.websocket_connect(url).__enter__()
        self._on_message = on_message

    def periodic(self, callback, interval) -> Periodic:
        return _StarletteTestPeriodic(callback=callback, interval=interval)

    async def write(self, message, binary=False, wait=True):
        if binary:
            self._ws.send_bytes(message)
        else:
            self._ws.send_text(message)

        # read back message
        self._on_message(self._ws.receive_text())

    async def close(self):
        try:
            self._ws.__exit__()
        except WebSocketDisconnect:
            return


class _PerspectiveStarletteTestClient(PerspectiveWebsocketClient):
    def __init__(self, test_client: TestClient):
        """Create a `PerspectiveStarletteTestClient` that interfaces with a Perspective server over a Websocket"""
        super(_PerspectiveStarletteTestClient, self).__init__(
            _PerspectiveStarletteWebsocketConnection(test_client)
        )


async def websocket(test_client: TestClient, url: str):
    """Create a new websocket client at the given `url` using the thread current
    tornado loop."""
    client = _PerspectiveStarletteTestClient(test_client)
    await client.connect(url)
    return client
