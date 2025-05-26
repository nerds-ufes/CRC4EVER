# from polka.tools import calculate_routeid, print_poly
import random
import bfrt_grpc.client as gc
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import time
import json
import sys

from case_functions import p4_functions as p4f  # No need for relative import
from case_functions import create_pkts as cp  # No need for relative import
from case_functions import sniff_pkts as sp  # No need for relative import

def gc_connect():
    try:
        interface = gc.ClientInterface(
            grpc_addr="localhost:50052",
            #client_id=,
            #device_id=0,
            #num_tries=1,
        )
    except Exception:
        sys.exit(1)
    dev_tgt = gc.Target(device_id=0, pipe_id=0xffff)
    bfrt_info = interface.bfrt_info_get()
    if bfrt_client_id == 0:
        interface.bind_pipeline_config(bfrt_info.p4_name_get())
    return interface, dev_tgt, bfrt_info


def main():
    interface, dev_tgt, bfrt_info = gc_connect()

    algorithm_tbl = bfrt_info.table_get("Ingress.hash.algorithm")
    data_field_list = [
	gc.DataTuple("polynomial",node_id_int), #node_id
    ]
    data_list = algorithm_tbl.make_data(data_field_list,"user_defined")
    algorithm_tbl.default_entry_set(dev_tgt, data_list)

if __name__ == "__main__":
    main()
