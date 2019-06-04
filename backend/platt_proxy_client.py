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

        self._loop = asyncio.get_event_loop()

        # create tasks for the individual connections
        new_file_information_connection_task = self._loop.create_task(
            self._new_file_information_connection_coro())
        index_connection_task = self._loop.create_task(
            self._index_connection_coro())

        # file_request_connection_task = self._loop.create_task(
        #     self._file_request_connection_coro())
        # file_answer_connection_task = self._loop.create_task(
        #     self._file_answer_connection_coro())

        file_download_task = self._loop.create_task(
            self._file_download_coro())

        # create a task that watches all connections
        connection_watchdog_task = self._loop.create_task(
            self._connection_watchdog_coro())


        # manage the queue cleanup when there are no active connections
        queue_cleanup_task = self._loop.create_task(
            self._queue_cleanup_coro())
        # shutdown_watch_task = self._loop.create_task(
        #     self._watch_shutdown_event_coro())

        self.tasks = [
            connection_watchdog_task,
            index_connection_task,

            file_download_task,

            # file_request_connection_task,
            # file_answer_connection_task,

            new_file_information_connection_task,
            queue_cleanup_task# ,
            # shutdown_watch_task
        ]

        try:
            # start the tasks
            self._loop.run_until_complete(asyncio.wait(self.tasks))
            if self._shutdown_client_event.wait():
                self.stop()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        gl.info("Shutdown client")
        self._loop.stop()

        for task in self.tasks:
            task.cancel()
            with suppress(asyncio.CancelledError):
                self._loop.run_until_complete(task)

        self._loop.close()


        # clear when shutdown complete
        self._shutdown_client_event.clear()
        gl.info("Client shutdown complete")

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
    # watch the shutdown event
    #
    async def _watch_shutdown_event_coro(self):
        """
        Watch the shutdown event and stop the client if shutdown is requested.

        """
        while True:

            if self._shutdown_client_event.is_set():
                self.stop()

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
        # remember which files we spotted in the queue how many times
        data_in_queue_occurences = dict()

        while True:

            new_data_in_queue_occurences = dict()

            if self._shutdown_client_event.is_set():
                return

            await asyncio.sleep(5)   # do this every five seconds

            # reset the index requests
            if not self._index_connection_active:
                self._get_index_event.clear()

            # clear the queue of things that are no longer needed
            #
            # this is of course a race condition with the actual file retrieval
            # but qsize is a bit slow, so I think this is fine
            data_queue_size = self._file_contents_name_hash_client_queue.qsize()

            for i in range(data_queue_size):
                try:
                    data = self._file_contents_name_hash_client_queue.get()
                except queue.Empty:
                    pass
                else:
                    data_name = data["file_request"]["object"]

                    try:
                        last_occ_count = data_in_queue_occurences[data_name]
                    except KeyError:
                        last_occ_count = 0

                    new_data_in_queue_occurences[data_name] = last_occ_count + 1

                    # reinsert into queue or delete it (don't reinsert)
                    if ((last_occ_count + 1) < 3):
                        self._file_contents_name_hash_client_queue.put(data)
                    else:
                        pass    # delete it

            data_queue_size = new_data_in_queue_occurences.copy()

    def _queue_cleanup_executor(self):
        """
        Run this in a separate executor.

        """
        while True:

            # repeat 1000 times per second, acts as rate throttling
            time.sleep(1e-3)

            if not self._new_file_information_connection_active:
                # nothing to do
                pass

            if not self._index_connection_active:
                self._get_index_event.clear()

            # if not self._file_request_connection_active:
            #     try:
            #         self._file_name_request_client_queue.get(False)
            #     except queue.Empty:
            #         pass

            # if not self._file_answer_connection_active:
            #     # nothing to do
            #     pass


    ##################################################################
    # handle the pushing of information about new files from the server
    #
    async def _new_file_information_connection_coro(self):
        """
        Handle information about new files from the server.

        """
        # try to maintain the connection
        while True:

            try:
                # open a connection
                gl.info("Attempting to open a connection for receiving "
                             "new file information")
                new_file_reader, new_file_writer = (
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
                    new_file_reader, new_file_writer, task_handshake)

                self._new_file_information_connection_active = True

                try:
                    while not new_file_reader.at_eof():
                        read_connection_task = self._loop.create_task(
                            self.read_new_file(new_file_reader, new_file_writer)
                        )
                        await read_connection_task

                except Exception as e:
                    gl.error("Exception in new_files: {}".format(e))

                finally:
                    new_file_writer.close()
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

        gl.info("New file from server: {}".format(res))
        self._new_file_receive_queue.put(res)


    ##################################################################
    # handle requesting the complete index from the ceph cluster
    #
    async def _index_connection_coro(self):
        """
        Handle index requests.

        """
        while True:
            try:
                # open a connection
                gl.info("Attempting to open a connection for receiving "
                             "the index")
                index_request_reader, index_request_writer = (
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
                    index_request_reader, index_request_writer, task_handshake)

                self._index_connection_active = True

                self._cancel_index_executor_event = threading.Event()

                index_connection_watchdog = self._loop.create_task(
                    self._watch_index_connection(
                        index_request_reader, index_request_writer))

                try:
                    while not index_request_reader.at_eof():
                        index_event_watch_task = self._loop.create_task(
                            self.watch_index_events(
                                index_request_reader, index_request_writer)
                        )
                        await index_event_watch_task

                except Exception as e:
                    gl.error("Exception in index: {}".format(e))

                finally:
                    index_request_writer.close()
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
        # self._index_pipe_remote.send(index)
        # self._index_avail_event.set()

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
                return
            await self.send_ack(writer)

            self._index_data_queue.put(index)


    ##################################################################
    # handle requests for files directly by opening a connection
    #
    async def _file_download_coro(self):
        """
        For every file request open a connection and answer directly.

        """
        while True:
            self._cancel_download_request_executor_event = threading.Event()

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

        gl.debug("Requested file data and hash")

        return file_request_in_queue

    def download_request_event_executor(self):
        """
        Watch the index events.

        """
        while True:

            time.sleep(1e-4)

            if self._cancel_download_request_executor_event.is_set():
                self._cancel_download_request_executor_event.clear()
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
            try:
                # open a connection
                gl.info("Attempting to open a connection for requesting files")
                file_request_reader, file_request_writer = (
                    await asyncio.open_connection(
                        self._host, self._port, loop=self._loop)
                )

            except (OSError, asyncio.TimeoutError):
                counter += 1
                if counter == 3:
                    gl.warning("Too many timeouts")
                    break

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
                    res["file_request"]["contents"] = base64.b64decode(
                        res["file_request"]["contents"].encode())
                    self._file_contents_name_hash_client_queue.put(res)

                except Exception as e:
                    gl.error("Exception in requests: {}".format(e))

                finally:
                    file_request_writer.close()
                    # self._file_request_connection_active = False
                    gl.info("Request connection closed")
                    break


    # ##################################################################
    # # handle requests for file contents from the server
    # #
    # async def _file_request_connection_coro(self):
    #     """
    #     Handle file requests from the server.

    #     """
    #     while True:
    #         try:
    #             # open a connection
    #             gl.info("Attempting to open a connection for requesting "
    #                          "files")
    #             file_request_reader, file_request_writer = (
    #                 await asyncio.open_connection(
    #                     self._host, self._port, loop=self._loop)
    #             )

    #         except (OSError, asyncio.TimeoutError):
    #             gl.info("Can't establish a connection to request files, "
    #                          "waiting a bit")
    #             await asyncio.sleep(3.5)

    #         else:
    #             # perform a handshake for this connection
    #             task_handshake_request = {"task": "file_requests"}
    #             await self.send_connection(
    #                 file_request_reader,
    #                 file_request_writer,
    #                 task_handshake_request
    #             )

    #             self._file_request_connection_active = True

    #             self._cancel_file_request_executor_event = threading.Event()

    #             file_request_connection_watchdog = self._loop.create_task(
    #                 self._watch_file_request_connection(
    #                     file_request_reader, file_request_writer))

    #             try:
    #                 while not file_request_reader.at_eof():
    #                     watch_file_request_queue_task = self._loop.create_task(
    #                         self.watch_file_request_queue(
    #                             file_request_reader, file_request_writer)
    #                     )
    #                     await watch_file_request_queue_task

    #             except Exception as e:
    #                 gl.error("Exception in requests: {}".format(e))

    #             finally:
    #                 file_request_writer.close()
    #                 self._file_request_connection_active = False
    #                 gl.info("Request connection closed")

    # async def _watch_file_request_connection(self, reader, writer):
    #     """
    #     Check the connection and set an event if it drops.

    #     """
    #     while True:
    #         if reader.at_eof():
    #             self._cancel_file_request_executor_event.set()
    #             return
    #         await asyncio.sleep(.1)

    # async def watch_file_request_queue(self, reader, writer):
    #     """
    #     Watch index events in a separate executor.

    #     """
    #     file_request_in_queue = await self._loop.run_in_executor(
    #         None, self.file_request_event_executor)

    #     if not file_request_in_queue:
    #         return None

    #     gl.info("Requested file data and hash")
    #     await self.send_connection(reader, writer, file_request_in_queue)

    # def file_request_event_executor(self):
    #     """
    #     Watch the index events.

    #     """
    #     while True:

    #         if self._cancel_file_request_executor_event.is_set():
    #             self._cancel_file_request_executor_event.clear()
    #             return None

    #         try:
    #             push_file = self._file_name_request_client_queue.get(True, .1)
    #         except queue.Empty:
    #             pass
    #         else:
    #             return push_file


    # ##################################################################
    # # handle answers to requests for file contents from the server
    # #
    # async def _file_answer_connection_coro(self):
    #     """
    #     Handle answers to file requests from the server.

    #     """
    #     while True:
    #         try:
    #             # open a connection
    #             gl.info("Attempting to open a connection for receiving "
    #                          "requested files")
    #             file_answer_reader, file_answer_writer = (
    #                 await asyncio.open_connection(
    #                     self._host, self._port, loop=self._loop)
    #             )

    #         except (OSError, asyncio.TimeoutError):
    #             gl.info("Can't establish a connection to receive "
    #                          "requested files, waiting a bit")
    #             await asyncio.sleep(3.5)

    #         else:
    #             # perform a handshake for this connection
    #             task_handshake_answer = {"task": "file_answers"}
    #             await self.send_connection(
    #                 file_answer_reader, file_answer_writer, task_handshake_answer)

    #             self._file_answer_connection_active = True

    #             try:
    #                 while not file_answer_reader.at_eof():
    #                     watch_file_request_server_answer_task = (
    #                         self._loop.create_task(
    #                             self.watch_file_request_server_answer(
    #                                 file_answer_reader, file_answer_writer)
    #                         )
    #                     )
    #                     await watch_file_request_server_answer_task

    #             except Exception as e:
    #                 gl.error("Exception in requests: {}".format(e))

    #             finally:
    #                 file_answer_writer.close()
    #                 self._file_answer_connection_active = False
    #                 gl.info("Answer connection closed")

    # async def watch_file_request_server_answer(self, reader, writer):
    #     """
    #     Watch index events in a separate executor.

    #     """
    #     res = await self.read_data(reader, writer)

    #     if not res:
    #         await self.send_nack(writer)
    #         return
    #     await self.send_ack(writer)
    #     res["file_request"]["value"] = base64.b64decode(
    #         res["file_request"]["value"].encode())
    #     self._file_contents_name_hash_client_queue.put(res)


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
        length_b = await reader.read(1024)

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
            data = await reader.readexactly(length)
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
        writer.write(binary_dictionary_length_encoded)
        await writer.drain()

        # check ack or nack
        is_ack = await self.check_ack(reader)
        if not is_ack:
            return False

        # send actual file
        writer.write(binary_dictionary)
        await writer.drain()

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
        ck = await reader.read(8)
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
        writer.write("ack".encode())
        await writer.drain()

    async def send_nack(self, writer):
        """
        Send an ACK.

        """
        writer.write("nack".encode())
        await writer.drain()
