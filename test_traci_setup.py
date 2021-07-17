import traci
import sumolib

import feature_extraction as fe

query = {
    "user_data": [
        {
            "feature": "count",
            "user_class": "passenger",
            "at": "phase",
            "mapping": {0: 'cars'}
        }],
    "tls_data": []
    }


sumo_bin_name = 'sumo'
sumo_bin = sumolib.checkBinary(sumo_bin_name)
traci.start([sumo_bin, "--net-file", "test/data/test.net.xml", "--route-files", "test/data/routes.rou.xml", "--start"])
traci.simulationStep()
pipeline = fe.TLSDataPipeline('C', -1, {'cars': 0}, query)
print(pipeline.extract())

traci.close()

