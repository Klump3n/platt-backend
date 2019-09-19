#! /usr/bin/env python3
"""
Start the proxy services.

Maintains an index and returns files from the platt proxy.

"""
import queue
import asyncio
import threading
from contextlib import suppress

from util.loggers import BackendLog as bl

import backend.proxy_services_data as pd
import backend.proxy_services_index as pi


class ProxyServices(object):
    """
    Starts the proxy services.

    """
    def __init__(self, comm_dict):
        bl.debug("Starting ProxyServices")

        self._comm_dict = comm_dict

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._pi = pi.ProxyIndex(self._loop, self._comm_dict)
        self._pd = pd.ProxyData(self._loop, self._comm_dict)

        watch_incoming_files_task = self._loop.create_task(
            self._pd._watch_incoming_files_coro())
        periodically_delete_files_task = self._loop.create_task(
            self._pd._periodic_file_deletion_coro())

        periodically_update_index_task = self._loop.create_task(
            self._pi._periodic_index_update_coro())
        watch_new_files_task = self._loop.create_task(
            self._pi._watch_new_files_coro())

        self._shutdown_event = self._comm_dict["shutdown_platt_gateway_event"]

        subscription_crawler_task = self._loop.create_task(
            pi._subscription_crawler_coro(self._shutdown_event))

        self._tasks = [
            watch_incoming_files_task,
            periodically_delete_files_task,
            periodically_update_index_task,
            watch_new_files_task,
            subscription_crawler_task
        ]

        try:
            # start the tasks
            self._loop.run_until_complete(asyncio.wait(self._tasks))

        except KeyboardInterrupt:
            pass

        finally:

            self._loop.stop()

            all_tasks = asyncio.Task.all_tasks()

            for task in all_tasks:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    self._loop.run_until_complete(task)

            self._loop.close()

            bl.debug("ProxyServices is shut down")


def index(namespace=None):
    """
    Obtain the index of the ceph cluster.

    Note: this is an async function so that we can perform this action in
    parallel.

    """
    return pi.index(namespace=namespace)


def subscribe(source_dict=None):
    """
    Get the most recent timestep for the selected namespace/field/geometry.

    """
    pass


def simulation_file(source_dict=None, namespace=None, object_key_list=[]):
    """
    Obtain a simulation file from the ceph cluster.

    Note: this is an async function so that we can perform this action in
    parallel.

    """
    return pd.simulation_file(source_dict=source_dict, namespace=namespace,
                              object_key_list=object_key_list)
