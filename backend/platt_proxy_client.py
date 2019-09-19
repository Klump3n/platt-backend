#!/usr/bin/env python3
"""
The client for the platt-ceph-proxy.

Needed when the simulation data and index has to come from the ceph instance.

Client connects to server via one port. Server can always push messages to the
client, client can always request stuff from the server and gets it delivered in
reasonable time.

"""
import json
import time
import struct
import asyncio
import socket
import threading
import base64
import logging
import queue
from contextlib import suppress

# from util.loggers import CoreLog as cl, BackendLog as bl, SimulationLog as sl
from util.loggers import GatewayLog as gl

class Client(object):
    def __init__(
            self,
            host, port,
            proxy_connection_active_event,
            new_file_receive_queue,
            get_index_event,
            index_data_queue,
            # index_avail_event,
            # index_pipe_remote,
            file_name_request_client_queue,
            file_contents_name_hash_client_queue,
            shutdown_client_event
    ):
        gl.info("Client init")

        self._host = host
        self._port = port

        # set up queues and events
        self._proxy_connection_active_event = proxy_connection_active_event
        self._new_file_receive_queue = new_file_receive_queue
        self._get_index_event = get_index_event
        self._index_data_queue = index_data_queue
        # self._index_avail_event = index_avail_event
        # self._index_pipe_remote = index_pipe_remote
        self._file_name_request_client_queue = file_name_request_client_queue
        self._file_contents_name_hash_client_queue = file_contents_name_hash_client_queue
        self._shutdown_client_event = shutdown_client_event

        self._index_connection_active = False
        self._file_request_connection_active = False
        self._file_answer_connection_active = False
        self._new_file_information_connection_active = False

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # create tasks for the individual connections
        new_file_information_connection_task = self._loop.create_task(
            self._new_file_information_connection_coro())

        index_connection_task = self._loop.create_task(
            self._index_connection_coro())

        file_download_task = self._loop.create_task(
            self._file_download_coro())
        # save all the open write connections in a list so we can close it if
        # necessary
        self._file_download_writer_list = list()

        # create a task that watches all connections
        connection_watchdog_task = self._loop.create_task(
            self._connection_watchdog_coro())

        # manage the queue cleanup when there are no active connections
        queue_cleanup_task = self._loop.create_task(
            self._queue_cleanup_coro())

        shutdown_watch_task = self._loop.create_task(
            self._watch_shutdown_event_coro())

        self.tasks = [
            connection_watchdog_task,
            index_connection_task,

            file_download_task,

            new_file_information_connection_task,
            queue_cleanup_task,

            shutdown_watch_task
        ]

        try:
            # start the tasks
            self._loop.run_until_complete(asyncio.wait(self.tasks))

        except KeyboardInterrupt:
            pass

        finally:

            self._loop.stop()

            all_tasks = asyncio.Task.all_tasks()

            for task in all_tasks:
                # for task in self.tasks:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    self._loop.run_until_complete(task)

            self._loop.close()

            # clear when shutdown complete
            self._shutdown_client_event.clear()
            gl.info("Client shutdown complete")



    ##################################################################
    # watch the shutdown event
    #
    async def _watch_shutdown_event_coro(self):
        """
        Watch the shutdown event and stop the client if shutdown is requested.

        """
        # blocks until shutdown event is sent
        shutdown_event = await self._loop.run_in_executor(
            None, self._watch_shutdown_event_executor)

        gl.verbose("Client received shutdown event")

        # perform the shutdown duties, i.e. close all the tasks and connections
        #
        # close all connections
        self._new_file_writer.close()
        self._index_request_writer.close()
        for conn in self._file_download_writer_list:
            try:
                conn.close()
            except Exception as e:
                gl.debug_warning("Could not close file download writer, was "
                                 "probably closed")

    def _watch_shutdown_event_executor(self):
        """
        Wait for the shutdown event in a separate thread.

        """
        return self._shutdown_client_event.wait()

    ##################################################################
    # watch the connections to the proxy
    #
    async def _connection_watchdog_coro(self):
        """
        Watch all connections and set an event if all connections are active.

        """
        while True:

            if self._shutdown_client_event.is_set():
                return

            if (
                self._index_connection_active and
                self._new_file_information_connection_active
            ):
                if not self._proxy_connection_active_event.is_set():
                    self._proxy_connection_active_event.set()
            else:
                self._proxy_connection_active_event.clear()

            await asyncio.sleep(1e-1)


    ##################################################################
    # handle the cleanup of queues when connections are not active
    #
    async def _queue_cleanup_coro(self):
        """
        If there are no connections to the client the queues have to be emptied.

        If they are not then there will be an unnecessary burst of information
        on connection.

        """
        queue_cleanup = await self._loop.run_in_executor(
            None, self._queue_cleanup_executor)

    def _queue_cleanup_executor(self):
        """
        Run the queue cleanup in a separate thread.

        Do this because we would be blocking the thread when waiting for the
        shutdown event.

        """
        # remember which files we spotted in the queue how many times
        data_in_queue_occurences = dict()

        while True:

            # wait for 5 seconds, this is essentially a 5 second interval timer
            if self._shutdown_client_event.wait(5):
                return

            new_data_in_queue_occurences = dict()

            # reset the index requests
            if not self._index_connection_active:
                self._get_index_event.clear()

            # clear the queue of things that are no longer needed
            #
            # this is of course a race condition with the actual file retrieval
            # but qsize is a bit slow, so I think this is fine
            data_queue_size = self._file_contents_name_hash_client_queue.qsize()

            gl.debug("Data queue contains {} objects".format(data_queue_size))

            for i in range(data_queue_size):
                try:
                    data = self._file_contents_name_hash_client_queue.get()
                except queue.Empty:
                    pass
                else:
                    data_object = data["file_request"]["object"]
                    data_namespace = data["file_request"]["namespace"]

                    data_name = "{}/{}".format(data_namespace, data_object)

                    try:
                        last_occ_count = data_in_queue_occurences[data_name]
                    except KeyError:
                        last_occ_count = 0

                    new_data_in_queue_occurences[data_name] = last_occ_count + 1

                    # reinsert into queue or delete it (don't reinsert)
                    if ((last_occ_count + 1) < 3):
                        self._file_contents_name_hash_client_queue.put(data)
                    else:
                        gl.debug_warning("Removing {} from data "
                                         "queue".format(data_name))
                        pass    # delete it

            data_in_queue_occurences = new_data_in_queue_occurences.copy()

    ##################################################################
    # handle the pushing of information about new files from the server
    #
    async def _new_file_information_connection_coro(self):
        """
        Handle information about new files from the server.

        """
        # try to maintain the connection
        while True:

            if self._shutdown_client_event.is_set():
                return

            try:
                # open a connection
                gl.info("Attempting to open a connection for receiving "
                             "new file information")
                new_file_reader, self._new_file_writer = (
                    await asyncio.open_connection(
                        self._host, self._port, loop=self._loop)
                )

            except (OSError, asyncio.TimeoutError):
                gl.info("Can't establish a connection to receive new file "
                             "information, waiting a bit")
                await asyncio.sleep(3.5)

            else:
                # perform a handshake on this connection
                task_handshake = {"task": "new_file_message"}
                await self.send_connection(
                    new_file_reader, self._new_file_writer, task_handshake)

                self._new_file_information_connection_active = True

                try:
                    while not new_file_reader.at_eof():
                        read_connection_task = self._loop.create_task(
                            self.read_new_file(new_file_reader, self._new_file_writer)
                        )
                        await read_connection_task

                except ConnectionResetError as e:
                    if self._shutdown_client_event.is_set():
                        pass
                    else:
                        gl.error("New files connection reset: {}".format(e))

                except Exception as e:
                    gl.error("Exception in new_files: {}".format(e))

                finally:
                    self._new_file_writer.close()
                    self._new_file_information_connection_active = False
                    gl.info("New file connection closed")

    async def read_new_file(self, reader, writer):
        """
        Read a new file from the server.

        """
        res = await self.read_data(reader, writer)
        if not res:
            await self.send_nack(writer)
            return

        # send a final ack
        await self.send_ack(writer)

        # gl.debug("New file from server: {}".format(res["new_file"]))
        self._new_file_receive_queue.put(res["new_file"])


    ##################################################################
    # handle requesting the complete index from the ceph cluster
    #
    async def _index_connection_coro(self):
        """
        Handle index requests.

        """
        while True:

            if self._shutdown_client_event.is_set():
                return

            try:
                # open a connection
                gl.info("Attempting to open a connection for receiving "
                             "the index")
                index_request_reader, self._index_request_writer = (
                    await asyncio.open_connection(
                        self._host, self._port, loop=self._loop)
                )

            except (OSError, asyncio.TimeoutError):
                gl.info("Can't establish a connection to receive the "
                             "index, waiting a bit")
                await asyncio.sleep(3.5)

            else:
                # perform a handshake for this connection
                task_handshake = {"task": "index"}
                await self.send_connection(
                    index_request_reader, self._index_request_writer, task_handshake)

                self._index_connection_active = True

                self._cancel_index_executor_event = threading.Event()

                index_connection_watchdog = self._loop.create_task(
                    self._watch_index_connection(
                        index_request_reader, self._index_request_writer))

                try:
                    while not index_request_reader.at_eof():
                        index_event_watch_task = self._loop.create_task(
                            self.watch_index_events(
                                index_request_reader, self._index_request_writer)
                        )
                        await index_event_watch_task

                except ConnectionResetError as e:
                    if self._shutdown_client_event.is_set():
                        pass
                    else:
                        gl.error("Index connection reset: {}".format(e))

                except Exception as e:
                    gl.error("Exception in index: {}".format(e))

                finally:
                    self._index_request_writer.close()
                    self._index_connection_active = True
                    gl.info("Index connection closed")

    async def _watch_index_connection(self, reader, writer):
        """
        Check the connection and set an event if it drops.

        """
        while True:
            if reader.at_eof():
                self._cancel_index_executor_event.set()
                return
            await asyncio.sleep(.1)

    async def watch_index_events(self, reader, writer):
        """
        Watch index events in a separate executor.

        """
        get_index_event = await self._loop.run_in_executor(
            None, self.index_event_executor)

        if not get_index_event:
            return None

        gl.info("Index request received")

        index = await self.get_index(reader, writer)

        self._index_data_queue.put(index)

        return True             # something other than None

    def index_event_executor(self):
        """
        Watch the index events.

        """
        while True:

            if self._cancel_index_executor_event.is_set():
                self._cancel_index_executor_event.clear()
                return None

            get_index_event = self._get_index_event.wait(.1)

            if get_index_event:

                self._get_index_event.clear()
                return get_index_event
            else:
                pass

    async def get_index(self, reader, writer):
        """
        Write something over the connection.

        """
        dictionary = {"todo": "index"}

        gl.debug("Sending index request")
        if await self.send_connection(reader, writer, dictionary):

            gl.debug("Index request sent")

            index = await self.read_data(reader, writer)
            gl.debug("Index received")

            if not index:
                await self.send_nack(writer)

            await self.send_ack(writer)

            return index


    ##################################################################
    # handle requests for files directly by opening a connection
    #
    async def _file_download_coro(self):
        """
        For every file request open a connection and answer directly.

        """
        while True:

            if self._shutdown_client_event.is_set():
                return

            # self._cancel_download_request_executor_event = threading.Event()

            # figure out which file we want to download
            watch_download_request_queue_task = self._loop.create_task(
                self.watch_download_request_queue()
            )
            download_request = await watch_download_request_queue_task

            # download that file from the proxy
            file_download_task = self._loop.create_task(
                self._download_and_return_file(download_request)
            )

    async def watch_download_request_queue(self):
        """
        Watch index events in a separate executor.

        """
        file_request_in_queue = await self._loop.run_in_executor(
            None, self.download_request_event_executor)

        if file_request_in_queue is not None:
            gl.debug("Requested file data and hash")

        return file_request_in_queue

    def download_request_event_executor(self):
        """
        Watch the index events.

        Do this because we block when we get from the queue in a blocking
        fashion.

        """
        while True:

            if self._shutdown_client_event.is_set():
                return None

            try:
                push_file = self._file_name_request_client_queue.get(True, .1)
            except queue.Empty:
                pass
            else:
                return push_file

    async def _download_and_return_file(self, requested_file):
        """
        Request a file from a server.

        """
        counter = 0
        while True:

            if self._shutdown_client_event.is_set():
                return

            try:
                # open a connection
                gl.info("Attempting to open a connection for requesting files")
                file_request_reader, file_request_writer = (
                    await asyncio.open_connection(
                        self._host, self._port, loop=self._loop)
                )

                # store writer in list
                self._file_download_writer_list.append(file_request_writer)

            except (OSError, asyncio.TimeoutError):
                counter += 1
                if counter == 3:
                    gl.warning("Too many timeouts")
                    break

                self._file_download_writer_list.append(file_request_writer)

                gl.warning("Can't establish a connection to request files, "
                             "waiting a bit")
                await asyncio.sleep(3.5)

            else:
                try:
                    # perform a handshake for this connection
                    task_handshake_request = {"task": "file_download"}
                    await self.send_connection(
                        file_request_reader,
                        file_request_writer,
                        task_handshake_request
                    )

                    file_request_dict = {"requested_file": requested_file}
                    requested_descriptor = "{}/{}".format(
                        requested_file["namespace"],
                        requested_file["key"])

                    await self.send_connection(
                        file_request_reader,
                        file_request_writer,
                        file_request_dict
                    )

                    res = await self.read_data(file_request_reader, file_request_writer)

                    if not res:
                        await self.send_nack(file_request_writer)
                        return
                    await self.send_ack(file_request_writer)

                    object_descriptor = "{}/{}".format(
                        res["file_request"]["namespace"],
                        res["file_request"]["object"])

                    gl.debug("Received {}".format(object_descriptor))

                    if object_descriptor == requested_descriptor:
                        # decode the base64 contents
                        res["file_request"]["contents"] = base64.b64decode(
                            res["file_request"]["contents"].encode())
                        self._file_contents_name_hash_client_queue.put(res)
                        break

                    else:
                        gl.debug_warning("Not the requested file, trying again")

                except Exception as e:
                    gl.error("Exception in requests: {}".format(e))

                finally:
                    self._file_download_writer_list.remove(file_request_writer)
                    file_request_writer.close()
                    # self._file_request_connection_active = False
                    gl.info("Request connection closed")

    ##################################################################
    # utility functions for sending and receiving data to and from the client
    #
    async def read_data(self, reader, writer):
        """
        Read data from the connection.

        NOTE: Do not forget to send an ACK or NACK after using this method.
        Otherwise the connection might hang up.

        await self.send_ack(writer)
        await self.send_nack(writer)

        """
        # wait until we have read something that is up to 1k (until the newline
        # comes)
        try:
            length_b = await reader.read(1024)
        except ConnectionResetError as e:
            if self._shutdown_client_event.is_set():
                pass
            else:
                gl.warning("Connection reset while reading data")

        if reader.at_eof():
            return

        try:
            # try and parse it as an int (expecting the length of the data)
            length = struct.unpack("L", length_b)[0]
        except Exception as e:
            # if something goes wrong send a nack and start anew
            await self.send_nack(writer)
            gl.error("An Exception occured: {}".format(e))
            raise
            return
        else:
            # otherwise send the ack
            await self.send_ack(writer)

        try:
            # try and read exactly the length of the data
            try:
                data = await reader.readexactly(length)
            except ConnectionResetError as e:
                if self._shutdown_client_event.is_set():
                    pass
                else:
                    gl.warning("Connection reset while reading data")
            else:
                res = data.decode("UTF-8")
                res = json.loads(res)

        except json.decoder.JSONDecodeError:
            # if we can not parse the json send a nack and start from the
            # beginning
            gl.debug("Parsing {} as json failed".format(res))
            await self.send_nack(writer)
            raise
            return
        except Exception as e:
            # if ANYTHING else goes wrong send a nack and start from the
            # beginning
            await self.send_nack(writer)
            gl.error("An Exception occured: {}".format(e))
            raise
            return
        else:
            # otherwise return the received data
            return res

        # await self.send_ack(writer)
        # await self.send_nack(writer)
        # NOTE: do not forget to send a final ack or nack


    async def send_connection(self, reader, writer, dictionary):
        """
        Write something over the connection.

        """
        dictionary_str = json.dumps(dictionary)
        binary_dictionary = dictionary_str.encode()

        binary_dictionary_length = len(binary_dictionary)
        binary_dictionary_length_encoded = struct.pack(
            "L", binary_dictionary_length)

        # send length
        try:
            writer.write(binary_dictionary_length_encoded)
            await writer.drain()
        except ConnectionResetError as e:
            if self._shutdown_client_event.is_set():
                return
            else:
                gl.warning("Connection reset while sending data")
                return


        # check ack or nack
        is_ack = await self.check_ack(reader)
        if not is_ack:
            return False

        # send actual file
        try:
            writer.write(binary_dictionary)
            await writer.drain()
        except ConnectionResetError as e:
            if self._shutdown_client_event.is_set():
                return
            else:
                gl.warning("Connection reset while sending data")
                return

        # check ack or nack
        is_ack = await self.check_ack(reader)
        if not is_ack:
            return False

        return True


    ##################################################################
    # small helper functions for communication with the server
    #
    async def check_ack(self, reader):
        """
        Check for ack or nack.

        """
        try:
            ck = await reader.read(8)
        except ConnectionResetError as e:
            if self._shutdown_client_event.is_set():
                pass
            else:
                gl.warning("Connection reset while reading ACK")

        try:
            ck = ck.decode("UTF-8")
        except Exception as e:
            gl.error("An Exception occured: {}".format(e))
        else:
            if ck.lower() == "ack":
                return True
        return False

    async def send_ack(self, writer):
        """
        Send an ACK.

        """
        try:
            writer.write("ack".encode())
            await writer.drain()
        except ConnectionResetError as e:
            if self._shutdown_client_event.is_set():
                pass
            else:
                gl.warning("Connection reset while sending ACK")

    async def send_nack(self, writer):
        """
        Send an ACK.

        """
        try:
            writer.write("nack".encode())
            await writer.drain()
        except ConnectionResetError as e:
            if self._shutdown_client_event.is_set():
                pass
            else:
                gl.warning("Connection reset while sending NACK")
