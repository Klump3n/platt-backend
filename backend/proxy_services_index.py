#! /usr/bin/env python3
"""
Maintains the local index for the platt proxy.

"""
import queue
import asyncio
import threading
from contextlib import suppress

from util.loggers import BackendLog as bl


# for locking the LOCAL_INDEX dictionary (thread safety)
LI_LOCK = threading.Lock()

# make this file-globally available
LOCAL_INDEX = dict()


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
        global LI_LOCK
        global LOCAL_INDEX

        while True:

            get_index_event = self._comm_dict["get_index_event"]
            receive_index_data_queue = self._comm_dict["get_index_data_queue"]

            get_index_event.set()

            with LI_LOCK:

                try:
                    bl.debug("Waiting for index")
                    index = receive_index_data_queue.get(True, 5)

                except queue.Empty as e:
                    bl.debug_warning("Took more than 5 seconds to wait for "
                                     "index ({})".format(e))

                else:
                    LOCAL_INDEX = index["index"]

            if self._shutdown_event.wait(120):  # update every 2 minutes
                return


def index(namespace=None):
    """
    Obtain the index of the ceph cluster.

    Note: this is an async function so that we can perform this action in
    parallel.

    """
    global LI_LOCK
    global LOCAL_INDEX

    loc_ind = dict()
    with LI_LOCK:
        loc_ind = LOCAL_INDEX

    if namespace is not None:
        try:
            loc_ind = loc_ind[namespace]
        except KeyError:
            loc_ind = dict()

    return loc_ind


def subscribe():
    """
    Subscribe to the most recent timestep for a namespace/field/geometry.

    """
    pass
