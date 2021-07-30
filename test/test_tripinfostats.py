import unittest
import os
import xml.etree.ElementTree as ET
import metrics.tripinfostats as tis

class TestTripInfoStats(unittest.TestCase):
    """
    Test cases for metrics.tripinfostats
    """
    maxDiff = None # to see full assertion diff

    base_dir = os.path.dirname(os.path.realpath(__file__))
    trips_no_emissions = os.path.join(
        base_dir, "data", "metrics", "tripinfo.xml")
    trips_emissions = os.path.join(
        base_dir, "data", "metrics", "tripinfo_with_emit.xml")
    n_peds = 5
    n_vehs = 16
    n_cycs = 2

    def test_personinfo_to_dict(self):
        root = ET.parse(self.trips_emissions).getroot()
        result = tis.personinfo_to_dict(root[0])
        expected = {
            "id": "1",
            "type": "DEFAULT_PEDTYPE",
            "depart": "5.00",
            "departPos": "0.00",
            "arrival": "30.00",
            "arrivalPos": "26.20",
            "duration": "25.00",
            "routeLength": "26.20",
            "timeLoss": "2.30",
            "maxSpeed": "1.15"
        }
        self.assertDictEqual(result, expected)

    def test_tripinfo_to_dict(self):
        root = ET.parse(self.trips_no_emissions).getroot()
        result = tis.tripinfo_to_dict(root[1])

        expected = {
            "id":"0",
            "depart":"0.00",
            "departLane":"NN_2",
            "departPos":"5.10",
            "departSpeed":"0.00",
            "departDelay":"0.00",
            "arrival":"39.00",
            "arrivalLane":"CE_2",
            "arrivalPos":"184.40",
            "arrivalSpeed":"13.89",
            "duration":"39.00",
            "routeLength":"462.30",
            "waitingTime":"0.00",
            "waitingCount":"0",
            "stopTime":"0.00",
            "timeLoss":"6.83",
            "rerouteNo":"1",
            "devices":"tripinfo_0 routing_0",
            "vType":"DEFAULT_VEHTYPE",
            "speedFactor":"1.06",
            "vaporized":"",
            "emissions": {}
        }
        
        self.assertDictEqual(result, expected)

        root = ET.parse(self.trips_emissions).getroot()
        result = tis.tripinfo_to_dict(root[1])
        expected["devices"]+= " emissions_0"
        emit_part = {
            "emissions": {
                "CO_abs":"2127.905867",
                "CO2_abs":"134273.117954",
                "HC_abs":"12.883463",
                "PMx_abs":"2.562863",
                "NOx_abs":"56.025742",
                "fuel_abs":"57.718043",
                "electricity_abs":"0"
            }
        }
        expected.update(emit_part)
        self.assertDictEqual(result, expected)

    def test_get_personinfos(self):
        root = ET.parse(self.trips_emissions).getroot()
        result = tis.get_all_personinfos(root)
        result_ids = [r["id"] for r in result]

        expected_ids = ["1", "3", "0", "6", "16"]
        self.assertEqual(len(result), self.n_peds)
        self.assertEqual(result_ids, expected_ids)

    def test_get_tripinfos(self):
        root = ET.parse(self.trips_emissions).getroot()
        result = tis.get_all_tripinfos(root)
        result_ids = [r["id"] for r in result]

        expected_ids = [
            "0", "6", "c5", "3", "11", "9",
            "14", "7", "c2", "8", "12", "23",
            "24", "5", "1", "16", "2", "10"
        ]
        self.assertEqual(len(result), self.n_vehs + self.n_cycs)
        self.assertEqual(result_ids, expected_ids)

    def test_organize_by(self):
        root = ET.parse(self.trips_emissions).getroot()
        result = tis.get_all_tripinfos(root)