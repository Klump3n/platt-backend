#! /usr/bin/env python3
"""
Maintains the local index for the platt proxy.

"""
import re
import queue
import asyncio
import threading
from contextlib import suppress

import backend.util.recursive_dict_update as rcu
import backend.util.nested_dict_check as ndc

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
                    index = receive_index_data_queue.get(True, 100)

                except queue.Empty as e:
                    bl.warning("Took more than 100 seconds to wait for "
                               "index ({}). There will be nothing on display "
                               "here.".format(e))

                else:
                    LOCAL_INDEX = index["index"]

            # if self._shutdown_event.wait(120):  # update every 2 minutes
            if self._shutdown_event.wait():  # wait forever, do not periodically update the index
                return

    async def _watch_new_files_coro(self):
        """
        Watch for new files to add to the index.

        """
        new_files = await self._loop.run_in_executor(
            None, self._watch_new_files_executor)

    def _watch_new_files_executor(self):
        """
        Watch for new files to add to the index.

        Executor thread.

        """
        global LI_LOCK
        global LOCAL_INDEX

        new_file_queue = self._comm_dict["tell_new_file_queue"]

        while True:

            if self._shutdown_event.is_set():
                return

            try:
                new_file = new_file_queue.get(True, .1)  # block for 0.1 seconds
            except queue.Empty as e:
                pass
            else:
                update_dict = self._create_index_entry_from_new_file_dict(new_file)

                # bl.debug("Adding {}".format(update_dict))

                with LI_LOCK:
                    # this updates the LOCAL_INDEX with the dictionary
                    # update_dict
                    # update_dict may also be nested
                    rcu.update(LOCAL_INDEX, update_dict)

    @staticmethod
    def _create_dict_from_key(key, sha1sum=None):
    # def _create_dict_from_key(self, key, sha1sum=None):
        """
        Create a dictionary from a key.

        TODO: Refactor this.

        """
        simtype = None
        to_parse = None
        field_type = None
        fieldname = None
        skintype = None
        elemtype = None

        return_dict = dict()

        try:
            string = key.split("universe.fo.")[1]
            objects, timestep = string.split("@")

            objects_definition = objects.split(".")

            simtype = objects_definition[0]
            if simtype not in ["ta", "ma"]:
                raise ValueError

            # parse mesh or field, only field has field_type
            if objects_definition[1] in ["nodal", "elemental"]:
                to_parse = "field"
            else:
                to_parse = "mesh"

            if to_parse == "field":
                usage = objects_definition[1]
                fieldname = objects_definition[2]
                try:
                    elemtype = objects_definition[3]
                except IndexError:
                    pass

            elif to_parse == "mesh":
                usage = objects_definition[1]

                if usage == "nodes":
                    pass

                elif usage == "elements":
                    elemtype = objects_definition[2]

                elif usage == "skin":
                    skintype = objects_definition[2]
                    elemtype = objects_definition[3]

                elif usage == "elementactivationbitmap":
                    elemtype = objects_definition[2]

                elif usage == "elset":
                    fieldname = objects_definition[2]
                    elemtype = objects_definition[3]

                elif usage == "nset":
                    fieldname = objects_definition[2]

                elif usage == "boundingbox":
                    pass

            else:
                # not possible
                return None

        except Exception as e:
            return None

        return_dict[timestep] = {}

        return_dict[timestep][simtype] = {}

        return_dict[timestep][simtype][usage] = {}

        if usage in ["nodes", "boundingbox"]:
            i_entry = return_dict[timestep][simtype][usage]

        if usage in ["elements", "elementactivationbitmap"]:
            return_dict[timestep][simtype][usage][elemtype] = {}
            i_entry = return_dict[timestep][simtype][usage][elemtype]

        if usage == "skin":
            return_dict[timestep][simtype][usage][skintype] = {}
            return_dict[timestep][simtype][usage][skintype][elemtype] = {}
            i_entry = return_dict[timestep][simtype][usage][skintype][elemtype]

        if usage in ["elemental", "elset"]:
            return_dict[timestep][simtype][usage][fieldname] = {}
            return_dict[timestep][simtype][usage][fieldname][elemtype] = {}
            i_entry = return_dict[timestep][simtype][usage][fieldname][elemtype]

        if usage in ["nodal", "nset"]:
            return_dict[timestep][simtype][usage][fieldname] = {}
            i_entry = return_dict[timestep][simtype][usage][fieldname]

        i_entry['object_key'] = key
        i_entry['sha1sum'] = sha1sum

        return return_dict

    def _create_index_entry_from_new_file_dict(self, new_file_dict):
        """
        Create a dictionary entry from the new file dictionary.

        TODO: Refactor this.

        """
        key = new_file_dict["key"]
        namespace = new_file_dict["namespace"]
        sha1sum = new_file_dict["sha1sum"]

        key_dict = self._create_dict_from_key(key, sha1sum=sha1sum)

        if key_dict is not None:

            return_dict = dict()
            return_dict[namespace] = key_dict

        else:
            bl.debug("Can not add file {}/{}".format(namespace, key))
            return

        return return_dict

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


# dict contains dictionaries with the queue to send the update to and the
# criterion which has to be fulfilled (i.e. all the files that need to be
# present and the current timestep)
SUBSCRIPTION_DICT = dict()

# lock for the subscription dict
SD_LOCK = threading.Lock()      # do I even need this?

async def _subscription_crawler_coro(shutdown_event):
    """
    Iterate over all subscriptions and see if the required files are available.

    """
    global LI_LOCK
    global LOCAL_INDEX
    global SUBSCRIPTION_DICT
    global SD_LOCK

    # done here because of circular import stuff
    import backend.global_settings as gloset

    while True:

        await asyncio.sleep(1)  # wait one second

        with SD_LOCK:

            for subscription in list(SUBSCRIPTION_DICT.keys()):  # make a list so we can modify the original dictionary
                try:
                    delete = SUBSCRIPTION_DICT[subscription]["delete"]
                except KeyError:
                    pass
                else:
                    del SUBSCRIPTION_DICT[subscription]
                    bl.debug("Deleted {} from subscription dict".format(subscription))

        with SD_LOCK:

            for subscription in SUBSCRIPTION_DICT.keys():

                bl.debug("Checking subscription {}".format(subscription))

                value = SUBSCRIPTION_DICT[subscription]

                try:
                    _ = value["delete"]
                    bl.debug("Skipping {}, delete flag detected".format(subscription))

                except KeyError:

                    bl.debug("Handling subscription {}".format(subscription))

                    namespace = value["namespace"]

                    scene_hash = value["scene_hash"]
                    dataset_hash = subscription

                    with LI_LOCK:
                        bl.debug("Obtaining available timesteps")
                        avail_timesteps = list(LOCAL_INDEX[namespace].keys())
                        bl.debug("... found {}".format(len(avail_timesteps)))

                    # sorting from...
                    # https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
                    # neat.
                    convert = lambda text: int(text) if text.isdigit() else text.lower()
                    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
                    sorted_timesteps = sorted(avail_timesteps, key=alphanum_key)

                    bl.debug("Timesteps sorted")

                    # if current timestep is in sorted_timesteps  ...
                    current_timestep = value["dataset_object"].timestep()

                    try:
                        index = sorted_timesteps.index(current_timestep)
                        # index = sorted_timesteps.index(value["timestep"])
                        bl.debug("Found {} in timestep list at position {}".format(current_timestep, index))

                    except ValueError:
                        # current timestep is not in list... weird
                        # go back to start of loop
                        bl.debug("Could not find {} in timestep list".format(current_timestep))
                        continue

                    # check the last and second to last timestep
                    last_timestep = sorted_timesteps[-1]
                    bl.debug("Last timestep is {}".format(last_timestep))

                    # ... and not the last position
                    if sorted_timesteps[index] == last_timestep:
                        # is last in timestep list, nothing to do
                        bl.debug("Index position {} is the last timestep, no update required".format(index))
                        continue

                    check_dicts = list()

                    # check if the files we need are in the most recent timestep
                    for object_dict in value["object_dicts"]:
                        target = {namespace: {last_timestep: object_dict}}
                        check_dicts.append(target)

                    data_avail = True

                    with LI_LOCK:
                        for check_dict in check_dicts:
                            bl.debug("Checking for {} in local index".format(check_dict))
                            avail = ndc.contains(LOCAL_INDEX, check_dict)
                            if not avail:
                                bl.debug_warning("Not found, can't update to most recent timestep")
                                data_avail = False

                    if data_avail:
                        # set the timestep
                        bl.debug("Found all necessary files for most recent timestep")
                        dataset_timesteps = gloset.scene_manager.dataset_timesteps(
                            scene_hash, dataset_hash, set_timestep=last_timestep)
                        continue

                    else:

                        bl.debug("Did not find all necessary files for most recent timestep, checking for files in second to last timestep")

                        try:
                            second_last_timestep = sorted_timesteps[-2]
                        except:
                            bl.debug_warning("Could not find second to last timestep")
                            continue

                        # ... and not the second to last position
                        if sorted_timesteps[index] == second_last_timestep:
                            # is second to last in timestep list, nothing to do
                            bl.debug("We are already at the second to last timestep, nothing to do")
                            continue

                        check_dicts = list()

                        # check if the files we need are in the most recent timestep
                        for object_dict in value["object_dicts"]:
                            check_dicts.append({namespace: {second_last_timestep: object_dict}})

                        second_data_avail = True

                        with LI_LOCK:
                            for check_dict in check_dicts:
                                bl.debug("Checking for {} in local index".format(check_dict))
                                avail = ndc.contains(LOCAL_INDEX, check_dict)
                                if not avail:
                                    bl.debug_warning("Not found, can't update to most recent timestep")
                                    second_data_avail = False

                        if second_data_avail:
                            bl.debug("Found all necessary files for second to last timestep")
                            dataset_timesteps = gloset.scene_manager.dataset_timesteps(
                                scene_hash, dataset_hash, set_timestep=second_last_timestep)

# def _subscribe(dataset_hash, scene_hash, namespace, timestep, object_list):
def _subscribe(dataset_hash, scene_hash, namespace, dataset_object, object_list):
    """
    Subscribe to ONE update for the most recent timestep for the given
    parameters.

    Returns a new queue that will yield exactly one timestep. If the most
    recent timestep in the index is newer than the provided timestep it will
    return the most recent timestep immediately, otherwise it will yield the
    most recent timestep once all the files are available for it.

    """
    global LI_LOCK
    global LOCAL_INDEX
    global SUBSCRIPTION_DICT
    global SD_LOCK

    subscription = dict()

    # create a dictionary of files that need to be present in the new timestep
    object_dict_list = list()

    for key in object_list:
        key_dict = ProxyIndex._create_dict_from_key(key, sha1sum=None).values()
        object_dict_list.append(list(key_dict)[0])

    # subscription["timestep"] = timestep
    subscription["dataset_object"] = dataset_object
    subscription["namespace"] = namespace
    subscription["object_dicts"] = object_dict_list
    subscription["scene_hash"] = scene_hash

    with SD_LOCK:
        SUBSCRIPTION_DICT[dataset_hash] = subscription

def _unsubscribe(dataset_hash):
    """
    Unsubscribe from timestep updates.

    """
    with SD_LOCK:
        try:
            subscription = SUBSCRIPTION_DICT[dataset_hash]
        except KeyError:
            pass
        else:
            bl.debug("Setting delete flag")
            subscription["delete"] = True

# def subscribe(dataset_hash, scene_hash, namespace, timestep, object_list):
def subscribe(dataset_hash, scene_hash, namespace, dataset_object, object_list):
    """
    Subscribe to the most recent timestep for a namespace/field/geometry.

    """
    # _subscribe(dataset_hash, scene_hash, namespace, timestep, object_list)
    _subscribe(dataset_hash, scene_hash, namespace, dataset_object, object_list)

def unsubscribe(dataset_hash):
    """
    Unsubscribe from timestep updates.

    """
    _unsubscribe(dataset_hash)
