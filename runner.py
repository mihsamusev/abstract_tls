import sys

from sumolib import checkBinary
import traci

from tlsagents.base import TLSFactory
from resultlogger import get_logger
import configparser as cp


def run(tls_list, logger=None, debug_tls=None):
    """
    Main simulation loop
    """
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        time = traci.simulation.getTime()
        print("Time: {}".format(time))

        for tls in tls_list:
            tls.update_state()
            print("\t{} {}".format(tls.get_state_dict(), tls.get_variables()))
        
            # log tls states
            if logger:
                logger.info('%s', {"time": time, "states": tls.get_state_dict()})
    
            # debug data
            #if tls.tls_id in debug_tls:
                #tls.debug()

    # finalize
    sys.stdout.flush()
    traci.close()


if __name__ == "__main__":
    # read job configuration
    cfg = cp.get_valid_config()

    # Initialize SUMO simulator
    sumo_bin_name = 'sumo-gui' if cfg.sumo.gui else 'sumo'
    sumo_bin = checkBinary(sumo_bin_name)
    traci.start([sumo_bin, "-c", cfg.sumo.sumocfg])

    # this is build with a bulder design pattern from config
    tls_list = []
    for tls_cfg in cfg.tls:
        tls_type = tls_cfg.controller
        kwargs = {
            "tls_id": tls_cfg.id,
            "constants": tls_cfg.constants,
            "variables": tls_cfg.variables,
            "data_query": tls_cfg.extract
        }
        tls = TLSFactory.create_agent(tls_type, **kwargs)
        tls_list.append(tls)

    #tls_logger = get_logger("test", directory="/home/msa/Documents/SUMO/abstract_tls/log", is_timestamped=True)
    tls_logger = None
    run(tls_list, logger=None, debug_tls=False)


