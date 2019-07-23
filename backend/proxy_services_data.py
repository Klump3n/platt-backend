#! /usr/bin/env python3
"""
Obtains data from the ceph proxy.

"""
import time
import queue
import asyncio
import threading
from contextlib import suppress

from util.loggers import BackendLog as bl


# for locking the GATEWAY_DATA dictionary (thread safety)
GW_LOCK = threading.Lock()

# make this file-globally available
GATEWAY_DATA = dict()
# formatting of GATEWAY_DATA is as follows:
# GATEWAY_DATA = {namespace/object: {timestamp, request_dict}, ...}
# every file that comes in via the gateway will be dropped in this dictionary
# after a certain time the data will be deleted again to keep memory consumption
# down


class ProxyData(object):
    """
    Obtains data from the proxy.

    """
    def __init__(self, event_loop, comm_dict):

        self._loop = event_loop
        self._comm_dict = comm_dict

        self._shutdown_event = comm_dict["shutdown_platt_gateway_event"]
        self._file_request_answer_queue = comm_dict["file_contents_name_hash_queue"]

    async def _watch_incoming_files_coro(self):
        """
        Start the watcher in an executor.

        """
        file_watcher = await self._loop.run_in_executor(
            None, self._watch_incoming_files_executor)

    def _watch_incoming_files_executor(self):
        """
        Enter new files into the global list.

        """
        while True:

            if self._shutdown_event.is_set():
                return

            try:
                ans = self._file_request_answer_queue.get(True, .1)

            except queue.Empty:
                pass

            else:
                request_dict = ans["file_request"]
                obj_key = request_dict["object"]
                obj_namespace = request_dict["namespace"]

                object_descriptor = "{}/{}".format(obj_namespace, obj_key)
                bl.debug("Reading {} and making available".format(
                    object_descriptor))

                occurence_key = object_descriptor
                occurence_dict = {
                    "timestamp": time.time(),
                    "request_dict": request_dict
                }

                with GW_LOCK:
                    GATEWAY_DATA[occurence_key] = occurence_dict

    async def _periodic_file_deletion_coro(self):
        """
        Periodically delete old data in the GATEWAY_DATA dictionary.

        The starter.

        """
        file_deletion = await self._loop.run_in_executor(
            None, self._periodic_file_deletion_executor)

    def _periodic_file_deletion_executor(self):
        """
        Periodically delete old data in the GATEWAY_DATA dictionary.

        The executor.

        """
        while True:

            # wait for 1 second, this is essentially a 1 second interval timer
            if self._shutdown_event.wait(1):
                return

            current_time = time.time()

            with GW_LOCK:
                for object_descriptor in list(GATEWAY_DATA.keys()):

                    timestamp = GATEWAY_DATA[object_descriptor]["timestamp"]
                    elapsed_time = current_time - timestamp

                    if (elapsed_time > 60):

                        bl.debug("Removing {} after 60 seconds".format(
                            object_descriptor))
                        del GATEWAY_DATA[object_descriptor]


def simulation_file(source_dict=None, namespace=None, object_key_list=[]):
    """
    Obtain a simulation file from the ceph cluster.

    Note: this is an async function so that we can perform this action in
    parallel.

    """
    bl.debug("Requesting {} in namespace {}".format(object_key_list, namespace))

    expectation_list = list()
    for item in object_key_list:
        expectation_list.append("{}/{}".format(namespace, item))

    occurence_dict = dict()

    comm_dict = source_dict["external"]["comm_dict"]
    file_request_queue = comm_dict["file_request_queue"]
    file_request_answer_queue = comm_dict["file_contents_name_hash_queue"]

    before_qsize = file_request_answer_queue.qsize()
    if (before_qsize > 0):
        bl.debug_warning("Data return queue is not empty, contains {} "
                         "objects".format(before_qsize))

    # see if we have the data downloaded already, if not make the gateway client get it
    for obj in object_key_list:

        object_descriptor = "{}/{}".format(namespace, obj)

        with GW_LOCK:
            if object_descriptor in GATEWAY_DATA:
                bl.debug("Found {} in downloaded data, updating timestamp".format(object_descriptor))
                GATEWAY_DATA[object_descriptor]["timestamp"] = time.time()
            else:
                bl.debug("Downloading {}".format(object_descriptor))
                req = {"namespace": namespace, "key": obj}
                file_request_queue.put(req)


    # keep track how often we try to get data from the dictionary
    counter = 0

    # wait until we have everything downloaded
    while True:

        # wait a fraction of a second (rate throttling)
        time.sleep(.1)

        # do we have every file?
        all_present = True

        # get a list of keys in the GATEWAY_DATA
        with GW_LOCK:
            keys = list(GATEWAY_DATA.keys())

        for object_descriptor in expectation_list:

            if not object_descriptor in keys:
                all_present = False

            # update timestamp
            if object_descriptor in keys:
                with GW_LOCK:
                    GATEWAY_DATA[object_descriptor]["timestamp"] = time.time()

        # break the loop
        if all_present:
            bl.debug("Data complete")
            break

        counter += 1
        if (counter > 1000):    # very large meshes take some time
            bl.warning("Too many iterations. Could not get data from gateway.")
            return

    # prepare output of function
    res_bin = [None] * len(object_key_list)

    for object_descriptor in expectation_list:
        with GW_LOCK:
            GATEWAY_DATA[object_descriptor]["timestamp"] = time.time()
            request_dict = GATEWAY_DATA[object_descriptor]["request_dict"]

        obj_namespace = request_dict["namespace"]
        obj_key = request_dict["object"]

        bl.debug("Loading {}/{}".format(obj_namespace, obj_key))

        index = object_key_list.index(obj_key)
        res_bin[index] = request_dict

    return res_bin
