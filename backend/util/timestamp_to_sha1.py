#!/usr/bin/env python3
"""
Creates a SHA1 from the unix timestamp.

"""
import time
import hashlib


def timestamp_to_sha1():
    """
    This turns a linux timestamp into a sha1 hash, to uniquely identify a scene
    or a dataset based on the time it was created.

    """
    return hashlib.sha1(str(time.time()).encode('utf-8')).hexdigest()

