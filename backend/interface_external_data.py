#!/usr/bin/env python3
"""
The interface for acquiring simulation data from the ceph proxy server.

"""
import asyncio
import json
import hashlib
import struct
import time
import queue

from util.loggers import BackendLog as bl


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

def simulation_file(source_dict=None, namespace=None, object_key_list=[]):
    """
    Obtain a simulation file from the ceph cluster.

    Note: this is an async function so that we can perform this action in
    parallel.

    """
    expectation_list = object_key_list.copy()

    occurence_dict = dict()

    comm_dict = source_dict["external"]["comm_dict"]
    file_request_queue = comm_dict["file_request_queue"]
    file_request_answer_queue = comm_dict["file_contents_name_hash_queue"]

    for obj in object_key_list:
        req = {"namespace": namespace, "key": obj}
        file_request_queue.put(req)

    res_bin = [None] * len(object_key_list)

    counter = 0

    # print(expectation_list)

    while (len(expectation_list) > 0):

        # try and read from the data queue (coming from the proxy)
        try:
            ans = file_request_answer_queue.get(True, 10)
        except queue.Empty as e:
            bl.debug_warning("Took more than 10 seconds for a file to appear in queue. Aborting. ({})".format(e))
            break

        request_dict = ans["file_request"]
        obj_key = request_dict["object"]

        try:
            occurence_dict[obj_key] += 1
        except KeyError:
            occurence_dict[obj_key] = 1

        if obj_key in expectation_list:
            expectation_list.remove(obj_key)
            index = object_key_list.index(obj_key)
            res_bin[index] = request_dict["contents"]

        else:
            # if we keep getting the same file then it probably is not needed anymore
            if (occurence_dict[obj_key] < 100):
                # reinsert into queue
                file_request_answer_queue.put(ans)
            time.sleep(1e-2)    # don't spam

    return res_bin

    # while True:
    #     try:
    #         ans = file_request_answer_queue.get(True, 10)
    #     except queue.Empty as e:
    #         bl.debug_warning("Took more than 10 seconds for a file to appear in queue. Aborting. ({})".format(e))
    #         break
    #     counter += 1
    #     request_dict = ans["file_request"]
    #     obj_key = request_dict["object"]
    #     print(obj_key)
    #     index = object_key_list.index(obj_key)
    #     res_bin[index] = request_dict["contents"]
    #     if (counter == len(object_key_list)):
    #         break

    # return res_bin
