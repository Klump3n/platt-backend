#! /usr/bin/env python3
"""
Check if a nested dictionary is part of another dictionary.

"""
def contains(orig, look_for):
    """
    Look for look_for in the original dict orig.

    NOTE: This does not compare VALUES, only keys. We assume that if all keys
    are there, the value will be there too. This is a corner case for this
    program.

    """
    for k, v in look_for.items():
        if isinstance(v, dict):
            try:
                return contains(orig[k], v)
            except KeyError:
                # Key not in dict
                return False
        else:
            if k not in orig:
                return False
            else:
                pass
    return True


if __name__ == "__main__":
    """
    'Test' dict_contains.

    """
    a = {'ccphiam.s960ql.singlepass.coarse': {'000000000.000000': {'ta': {'nodes': {'object_key': 'universe.fo.ta.nodes@000000001.000000', 'sha1sum': None}}}}}
    b = {'ccphiam.s960ql.singlepass.coarse': {'000000000.000000': {'ta': {'nodes': {'object_key': 'universe.fo.ta.nodes@000000001.000000'}}}}}

    c = {'ccphiam.s960ql.singlepass.coarse': {'000000000.000000': {'ta': {'nodes': {'object_key': 'SOME_KEY'}}}}}
    d = {'ccphiam.s960ql.singlepass.coarse': {'000000000.000000': {'ta': {'nodes': {'object_key': 'SOME_OTHER_KEY'}}}}}

    e = {'ta': {'nodes': {'object_key': 'universe.fo.ta.nodes@000000001.000000', 'sha1sum': None}}}
    f = {'ta': {'nodes': {'object_key': '', 'sha1sum': None}}}

    assert(contains(a, a))
    assert(contains(a, b))
    assert(not contains(b, a))

    assert(contains(c, d))
    assert(contains(d, c))

    assert(contains(e, f))
    assert(contains(f, e))

    assert(not contains(a, e))
    assert(not contains(e, a))
