"""
Worker that receives input from Piped RDD.
"""
import sys
from base64 import standard_b64decode
# CloudPickler needs to be imported so that depicklers are registered using the
# copy_reg module.
from pyspark.broadcast import Broadcast, _broadcastRegistry
from pyspark.cloudpickle import CloudPickler
from pyspark.serializers import write_with_length, read_with_length, \
    read_long, read_int, dump_pickle, load_pickle, read_from_pickle_file


# Redirect stdout to stderr so that users must return values from functions.
old_stdout = sys.stdout
sys.stdout = sys.stderr


def load_obj():
    return load_pickle(standard_b64decode(sys.stdin.readline().strip()))


def main():
    split_index = read_int(sys.stdin)
    num_broadcast_variables = read_int(sys.stdin)
    for _ in range(num_broadcast_variables):
        bid = read_long(sys.stdin)
        value = read_with_length(sys.stdin)
        _broadcastRegistry[bid] = Broadcast(bid, load_pickle(value))
    func = load_obj()
    bypassSerializer = load_obj()
    if bypassSerializer:
        dumps = lambda x: x
    else:
        dumps = dump_pickle
    iterator = read_from_pickle_file(sys.stdin)
    for obj in func(split_index, iterator):
        write_with_length(dumps(obj), old_stdout)


if __name__ == '__main__':
    main()
