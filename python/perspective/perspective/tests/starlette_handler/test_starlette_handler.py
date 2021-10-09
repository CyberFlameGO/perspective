################################################################################
#
# Copyright (c) 2019, the Perspective Authors.
#
# This file is part of the Perspective library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#
import pytest
import random

from datetime import datetime

from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient

from perspective import Table, PerspectiveManager, PerspectiveStarletteHandler

from ...client.starlette_test import _PerspectiveStarletteTestClient, websocket


data = {
    "a": [i for i in range(10)],
    "b": [i * 1.5 for i in range(10)],
    "c": [str(i) for i in range(10)],
    "d": [datetime(2020, 3, i, i, 30, 45) for i in range(1, 11)],
}

MANAGER = PerspectiveManager()


async def websocket_handler(websocket: WebSocket):
    handler = PerspectiveStarletteHandler(MANAGER, websocket)
    await handler.run()


APPLICATION = FastAPI()
APPLICATION.add_api_websocket_route("/websocket", websocket_handler)

CLIENT = TestClient(APPLICATION)


class TestPerspectiveStarletteHandler(object):
    def setup_method(self):
        """Flush manager state before each test method execution."""
        MANAGER._tables = {}
        MANAGER._views = {}

    async def websocket_client(self):
        """Connect and initialize a websocket client connection to the
        Perspective tornado server.
        """
        return await websocket(CLIENT, "/websocket")

    @pytest.mark.asyncio
    async def test_starlette_handler_init_terminate(self):
        """Using FastAPI's builtin test client, test the websocket provided by
        PerspectiveStarletteHandler.

        All test methods must import `app`, `http_client`, and `http_port`,
        otherwise a mysterious timeout will occur."""
        client = await self.websocket_client()
        await client.terminate()

    @pytest.mark.asyncio
    async def test_starlette_handler_table_method(self):
        table_name = str(random.random())
        _table = Table(data)
        MANAGER.host_table(table_name, _table)

        client = await self.websocket_client()
        table = client.open_table(table_name)

        schema = await table.schema()
        size = await table.size()

        assert schema == {
            "a": "integer",
            "b": "float",
            "c": "string",
            "d": "datetime",
        }

        assert size == 10

        await client.terminate()

    # @pytest.mark.gen_test(run_sync=False)
    # def test_tornado_handler_make_table(self, app, http_client, http_port):
    #     client = yield self.websocket_client(http_port)
    #     table = yield client.table(data)
    #     size = yield table.size()

    #     assert size == 10

    #     table.update(data)

    #     size2 = yield table.size()
    #     assert size2 == 20

    # @pytest.mark.gen_test(run_sync=False)
    # def test_tornado_handler_table_update(self, app, http_client, http_port):
    #     table_name = str(random.random())
    #     _table = Table(data)
    #     MANAGER.host_table(table_name, _table)

    #     client = yield self.websocket_client(http_port)
    #     table = client.open_table(table_name)
    #     size = yield table.size()

    #     assert size == 10

    #     table.update(data)

    #     size2 = yield table.size()
    #     assert size2 == 20

    # @pytest.mark.gen_test(run_sync=False)
    # def test_tornado_handler_table_update_port(
    #     self, app, http_client, http_port, sentinel
    # ):
    #     table_name = str(random.random())
    #     _table = Table(data)
    #     MANAGER.host_table(table_name, _table)

    #     client = yield self.websocket_client(http_port)
    #     table = client.open_table(table_name)
    #     view = yield table.view()

    #     size = yield table.size()

    #     assert size == 10

    #     for i in range(5):
    #         yield table.make_port()

    #     port = yield table.make_port()

    #     s = sentinel(False)

    #     def updater(port_id):
    #         s.set(True)
    #         assert port_id == port

    #     view.on_update(updater)

    #     table.update(data, port_id=port)

    #     size2 = yield table.size()
    #     assert size2 == 20
    #     assert s.get() is True

    # @pytest.mark.gen_test(run_sync=False)
    # def test_tornado_handler_table_update_row_delta(
    #     self, app, http_client, http_port, sentinel
    # ):
    #     table_name = str(random.random())
    #     _table = Table(data)
    #     MANAGER.host_table(table_name, _table)

    #     client = yield self.websocket_client(http_port)
    #     table = client.open_table(table_name)
    #     view = yield table.view()

    #     size = yield table.size()

    #     assert size == 10

    #     s = sentinel(False)

    #     def updater(port_id, delta):
    #         s.set(True)
    #         t2 = Table(delta)
    #         assert t2.view().to_dict() == data
    #         assert port_id == 0

    #     view.on_update(updater, mode="row")

    #     table.update(data)

    #     size2 = yield table.size()
    #     assert size2 == 20
    #     assert s.get() is True

    # @pytest.mark.gen_test(run_sync=False)
    # def test_tornado_handler_table_update_row_delta_port(
    #     self, app, http_client, http_port, sentinel
    # ):
    #     table_name = str(random.random())
    #     _table = Table(data)
    #     MANAGER.host_table(table_name, _table)

    #     client = yield self.websocket_client(http_port)
    #     table = client.open_table(table_name)
    #     view = yield table.view()

    #     size = yield table.size()

    #     assert size == 10

    #     for i in range(5):
    #         yield table.make_port()

    #     port = yield table.make_port()

    #     s = sentinel(False)

    #     def updater(port_id, delta):
    #         s.set(True)
    #         t2 = Table(delta)
    #         assert t2.view().to_dict() == data
    #         assert port_id == port

    #     view.on_update(updater, mode="row")

    #     table.update(data, port_id=port)

    #     size2 = yield table.size()
    #     assert size2 == 20
    #     assert s.get() is True

    # @pytest.mark.gen_test(run_sync=False)
    # def test_tornado_handler_table_remove(self, app, http_client, http_port):
    #     table_name = str(random.random())
    #     _table = Table(data, index="a")
    #     MANAGER.host_table(table_name, _table)

    #     client = yield self.websocket_client(http_port)
    #     table = client.open_table(table_name)
    #     size = yield table.size()

    #     assert size == 10

    #     table.remove([i for i in range(5)])

    #     view = yield table.view(columns=["a"])
    #     output = yield view.to_dict()

    #     assert output == {"a": [i for i in range(5, 10)]}

    # @pytest.mark.gen_test(run_sync=False)
    # def test_tornado_handler_create_view(
    #     self, app, http_client, http_port, sentinel
    # ):
    #     table_name = str(random.random())
    #     _table = Table(data)
    #     MANAGER.host_table(table_name, _table)

    #     client = yield self.websocket_client(http_port)
    #     table = client.open_table(table_name)
    #     view = yield table.view(columns=["a"])
    #     output = yield view.to_dict()

    #     assert output == {
    #         "a": [i for i in range(10)],
    #     }

    # @pytest.mark.gen_test(run_sync=False)
    # def test_tornado_handler_create_view_errors(
    #     self, app, http_client, http_port, sentinel
    # ):
    #     table_name = str(random.random())
    #     _table = Table(data)
    #     MANAGER.host_table(table_name, _table)

    #     client = yield self.websocket_client(http_port)
    #     table = client.open_table(table_name)

    #     with pytest.raises(PerspectiveError) as exc:
    #         yield table.view(columns=["abcde"])

    #     assert str(exc.value) == "Invalid column 'abcde' found in View columns.\n"

    # @pytest.mark.gen_test(run_sync=False)
    # def test_tornado_handler_create_view_to_arrow(
    #     self, app, http_client, http_port, sentinel
    # ):
    #     table_name = str(random.random())
    #     _table = Table(data)
    #     MANAGER.host_table(table_name, _table)

    #     client = yield self.websocket_client(http_port)
    #     table = client.open_table(table_name)
    #     view = yield table.view()
    #     output = yield view.to_arrow()
    #     expected = yield table.schema()

    #     assert Table(output).schema(as_string=True) == expected

    # @pytest.mark.gen_test(run_sync=False)
    # def test_tornado_handler_create_view_to_arrow_update(
    #     self, app, http_client, http_port, sentinel
    # ):
    #     table_name = str(random.random())
    #     _table = Table(data)
    #     MANAGER.host_table(table_name, _table)

    #     client = yield self.websocket_client(http_port)
    #     table = client.open_table(table_name)
    #     view = yield table.view()

    #     output = yield view.to_arrow()

    #     for i in range(10):
    #         table.update(output)

    #     size2 = yield table.size()
    #     assert size2 == 110
