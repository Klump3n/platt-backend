#! /usr/bin/env python3
"""
Recursively update a dictionary.

Regular update may overwrite parts of the old dictionary and ruin it.

Found at https://stackoverflow.com/a/3233356

"""
import collections
import six

# python 3.8+ compatibility
try:
    collectionsAbc = collections.abc
except:
    collectionsAbc = collections

def update(d, u):
    for k, v in six.iteritems(u):
        dv = d.get(k, {})
        if not isinstance(dv, collectionsAbc.Mapping):
            d[k] = v
        elif isinstance(v, collectionsAbc.Mapping):
            d[k] = update(dv, v)
        else:
            d[k] = v
    return d
