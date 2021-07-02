import sys

from sumolib import checkBinary
import traci
from tlsagent import CrosswalkTLS, RecordedTLS, TimedTLS
from resultlogger import get_logger
from split_log import get_tls_dicts


def run(tls_list=[], logger=None):

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        time = traci.simulation.getTime()
        print("Time: {}".format(time))

        for tls in tls_list:
            tls.update_state()
            print("\t{} {}".format(tls.get_state_dict(), tls.get_variables()))
            if logger:
                logger.info('%s', {"time": time, "states": tls.get_state_dict()})
    
    # finalize
    sys.stdout.flush()
    traci.close()

if __name__ == "__main__":
        # Initialize SUMO simulator
    sumo_bin_name = 'sumo-gui' 
    sumo_bin = checkBinary(sumo_bin_name)
    traci.start([sumo_bin, "-c", "data/run.sumocfg"])

    # get precomputed logs
    precomputed_tls = get_tls_dicts("log/test_20210628141410.log")

    cfg = {
        "id": "B1",
        "constants": {"MIN_TIME": 15},
        "variables": {"ped_count": 0},
        "extract": [
            {"feature": "count",
            "user_type": "pedestrian",
            "from": "phase",
            "mapping": {2: "ped_count" }
            }]
        }

    # this is build with a bulder design pattern from config
    tls_list = [
        TimedTLS('A1'),
        CrosswalkTLS(cfg['id'], cfg["constants"], cfg["variables"], cfg["extract"]),
        RecordedTLS('C1', constants={"sequence": precomputed_tls["C1"]}),
    ]

    #tls_logger = get_logger("test", directory="/home/msa/Documents/SUMO/abstract_tls/log", is_timestamped=True)
    tls_logger = None
    run(tls_list, tls_logger)


