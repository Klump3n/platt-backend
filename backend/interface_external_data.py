#!/usr/bin/env python3
"""
The interface for acquiring simulation data from the ceph proxy server.

"""
import asyncio
import json
import hashlib
import struct

import queue
import multiprocessing

# async def _handshake(source_dict=None, action=None, namespace=None, object_key=None, loop=None):
#     """
#     Perform the handshake.

#     """
#     # Anything other than action='file' or action='index' will not work
#     if action not in ['index', 'file']:
#         return None

#     ext_addr = source_dict['external']['addr']
#     ext_port = source_dict['external']['port']

#     # Open a connection to the proxy program
#     reader, writer = await asyncio.open_connection(ext_addr, ext_port, loop=loop)

#     # Tell the proxy what we want to do
#     do_json = {'do': action}
#     if namespace == None:
#         namespace = ""
#     do_json['namespace'] = namespace
#     if action == 'file':
#         do_json['object_key'] = object_key
#     json_pkg = json.dumps(do_json)

#     json_pkg = json_pkg.encode()

#     length = struct.pack('L', len(json_pkg))

#     writer.write(length)
#     await writer.drain()

#     # Read an ACK
#     rx_str = await reader.read(8)  # Should be ACK or NACK
#     rx_str = rx_str.decode()
#     if rx_str != 'ACK':
#         return None

#     # Send the actual do:action JSON package
#     writer.write(json_pkg)
#     await writer.drain()

#     # Read an ACK
#     rx_str = await reader.read(8)  # Should be ACK or NACK
#     rx_str = rx_str.decode()
#     if rx_str != 'ACK':
#         return None

#     # Send an ACK to tell the proxy that we are ready do receive
#     writer.write('ACK'.encode())
#     await writer.drain()

#     # Read the length of whatever we are about to receive
#     rx_b = await reader.read(8)
#     rx_int = struct.unpack('L', rx_b)[0]

#     # Send an ACK
#     writer.write('ACK'.encode())
#     await writer.drain()

#     # Read the actual data
#     rx_b = await reader.readexactly(rx_int)

#     # Calculate the sha1 sum of the data
#     checksum = hashlib.sha1()
#     checksum.update(rx_b)
#     rx_b_sha1 = checksum.hexdigest()

#     # Write the sha1 sum back to the proxy to verify that we have received a
#     # flawless package
#     writer.write(rx_b_sha1.encode())
#     await writer.drain()

#     # Read an ACK
#     rx_str = await reader.read(8)  # Should be ACK or NACK
#     rx_str = rx_str.decode()
#     if rx_str != 'ACK':
#         return None

#     writer.close()

#     return rx_b

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
        index = receive_index_data_queue.get(True, 5)
    except queue.Empty:
        pass

    return index["index"]

def simulation_file(source_dict=None, namespace=None, object_key_list=[]):
    """
    Obtain a simulation file from the ceph cluster.

    Note: this is an async function so that we can perform this action in
    parallel.

    """
    comm_dict = source_dict["external"]["comm_dict"]
    file_request_queue = comm_dict["file_request_queue"]
    file_request_answer_queue = comm_dict["file_contents_name_hash_queue"]

    for obj in object_key_list:
        req = {"namespace": namespace, "key": obj}
        file_request_queue.put(req)

    res_bin = [None] * len(object_key_list)

    counter = 0

    while True:
        ans = file_request_answer_queue.get(True, 10)
        counter += 1
        request_dict = ans["file_request"]
        obj_key = request_dict["object"]
        index = object_key_list.index(obj_key)
        res_bin[index] = request_dict["contents"]
        if (counter == len(object_key_list)):
            break

    return res_bin
