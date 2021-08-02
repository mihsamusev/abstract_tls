import sys
import os
import argparse

import sumolib
import traci


from tlsagents.base import TLSFactory
from resultlogger import TLSLogger
import cfgparse


SUMO_GUI_CONFIG = "sumo_gui_config.xml"

def run(tls_list, logger, max_steps=10000):
    """
    Main simulation loop
    """
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
        # update simulation state
        traci.simulationStep()
        step += 1
        time = traci.simulation.getTime()

        # update tls state and data
        for tls in tls_list:
            tls.update_state()
        
            # log tls states
            if logger:
                if tls.tls_id in logger.tls_ids:
                    data_dict = tls.decsribe_step()
                    logger.log(time, data_dict)

        if logger:
            print()

    # finalize
    sys.stdout.flush()
    traci.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", type=str, required=True,
        help="yaml configuration file defining the simulation")
    args = ap.parse_args()
    cfg = cfgparse.get_valid_config(args)

    # validate nodes
    net = sumolib.net.readNet(cfg.sumo.network)
    valid_tls_id = [i.getID() for i in net.getTrafficLights()]
    for tls in cfg.tls:
        assert tls.id in valid_tls_id, \
        "@tls: TLS at node {} does not exist".format(tls.id)
    for tls_id in cfg.logging.ids:  
        assert tls_id in valid_tls_id, \
        "@logging: TLS at node {} does not exist".format(tls_id) 

    # Initialize SUMO simulator and prepare arguments
    sumo_bin_name = 'sumo-gui' if cfg.sumo.gui else 'sumo'
    sumo_bin = sumolib.checkBinary(sumo_bin_name)
    
    sumo_args = {
        "--net-file": cfg.sumo.network,
        "--additional-files": ",".join(cfg.sumo.additional),
        "--route-files": ",".join(cfg.sumo.route),
        "--gui-settings-file": SUMO_GUI_CONFIG,
        "--device.emissions.probability": "1.0",
        "--output-prefix": cfg.job.name + "_",
        "--tripinfo-output": os.path.join(cfg.logging.dir, "trips.xml"),
        "--vehroute-output": os.path.join(cfg.logging.dir, "vehroutes.xml"),
        "--queue-output": os.path.join(cfg.logging.dir, "queues.xml")
    }

    sumo_command = [sumo_bin]
    for k, v in sumo_args.items():
        if v:
            sumo_command.append(k)
            sumo_command.append(v)

    print("Starting simulation with:\n{}".format(" ".join(sumo_command)))
    traci.start(sumo_command)

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

    # create logger
    logger = None
    if cfg.get('logging'):
        logger = TLSLogger(
            cfg.job.name,
            cfg.logging.ids,
            cfg.logging.data,
            to_file=cfg.logging.to_file,
            to_console=cfg.logging.to_console,
            directory=cfg.logging.dir,
            is_timestamped=cfg.logging.timestamped
        )

    # simulate
    run(tls_list, logger, max_steps=cfg.sumo.max_steps)


