import os
import unittest

import traci
import sumolib

import feature_extraction as fe


class TestFeatureExtractionCrossing(unittest.TestCase):
    """
    Test cases for extracting data from SUMO
    """
    tls_id = 'C'
    base_dir = os.path.dirname(os.path.realpath(__file__))
    network_path = os.path.join(base_dir, "data", "test.net.xml")
    routes_path = os.path.join(base_dir, "data", "routes.rou.xml")

    def setUp(self):
        """
        Initialize SUMO, place cars where required
        """
        sumo_bin = sumolib.checkBinary('sumo')
        traci.start([sumo_bin, "-n", self.network_path, "-r", self.routes_path])
        traci.simulationStep()

    def tearDown(self):
        """
        Close connection to SUMO
        """
        traci.close()
    
    def test1(self):
        values = {"cars": 0}
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
        pipeline = fe.TLSDataPipeline('C', -1, values, query)
        result = pipeline.extract()
        self.assertDictEqual(result, {'cars': 3})
