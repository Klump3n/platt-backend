#! /usr/bin/env python3
"""
Maintains the local index for the platt proxy.

"""
import asyncio

from util.loggers import BackendLog as bl


class ProxyIndex(object):
    """
    Maintains a local index for the platt proxy.

    """
    def __init__(self, event_loop, comm_dict):
        bl.debug("Starting ProxyIndex")

        self._loop = event_loop
        self._comm_dict = comm_dict

        self._shutdown_event = comm_dict["shutdown_platt_gateway_event"]

    async def _periodic_index_update_coro(self):
        """
        Update the index in periodic intervals.

        """
        index_updater = await self._loop.run_in_executor(
            None, self._periodic_index_update_executor)

    def _periodic_index_update_executor(self):
        """
        Update the index in periodic intervals.

        Executor thread.

        """
        # have to import here because of circular import shenanigans
        import backend.global_settings as global_settings
        while True:

            if self._shutdown_event.wait(120):  # update every 2 minutes
                return

            _ = global_settings.scene_manager.ext_src_index(update=True)

def index(source_dict=None, namespace=None):
    """
    Obtain the index of the ceph cluster.

    Note: this is an async function so that we can perform this action in
    parallel.

    """
    comm_dict = source_dict["external"]["comm_dict"]
    get_index_event = comm_dict["get_index_event"]
    receive_index_data_queue = comm_dict["get_index_data_queue"]

    index = None

    get_index_event.set()

    try:
        bl.debug("Waiting for index")

        index = receive_index_data_queue.get(True, 5)

    except queue.Empty as e:
        bl.debug_warning("Took more than 5 seconds to wait for index. ({})".format(e))

    return index["index"]
