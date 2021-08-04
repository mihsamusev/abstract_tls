
from xml.etree.ElementTree import Element
import pandas as pd

def personinfo_to_dict(child: Element) -> dict:
    """
    Convers <personinfo> to dict only including walk tag
    """
    ped_data = child.attrib
    walk_element = child.find("walk")
    walk_data = {} if walk_element is None else walk_element.attrib
    ped_data.update(walk_data)
    return ped_data

def tripinfo_to_dict(child: Element) -> dict:
    """
    Convers <tripinfo> to dict info, includes emissions
    """
    trip_data = child.attrib
    emit_element = child.find("emissions")
    emit_data = {} if emit_element is None else emit_element.attrib 
    trip_data["emissions"] = emit_data
    return trip_data

def get_all_personinfos(root: Element) -> dict:
    """
    Converts tripinfo xml ElementTree list of person info dicts
    """
    result = []
    for child in root:
        if child.tag == "personinfo":
            d = personinfo_to_dict(child)
            result.append(d)
    return result


def get_all_tripinfos(root: Element) -> dict:
    """
    Converts tripinfo xml ElementTree list of trip info dicts
    """
    result = []
    for child in root:
        if child.tag == "tripinfo":
            d = tripinfo_to_dict(child)
            result.append(d)
    return result

def pedinfo_to_pandas(root: Element) -> dict:
    """
    attribute: edge, lane, vType, 
    """
    headers = ["type", "duration", "routeLength", "timeLoss"]
    for trip in get_all_personinfos(root):
        clean_trip = {}
        for k, v in trip.items():
            if k in headers:
                clean_trip[k] = v
        print(clean_trip)

def tripinfo_to_pandas(root: Element) -> dict:
    """
    attribute: edge, lane, vType, 
    """
    headers = ["vType", "duration", "routeLength", "waitingTime", "waitingCount", "timeLoss"]
    clean_trips = []
    for trip in get_all_tripinfos(root):
        clean_trip = {}
        for k, v in trip.items():
            if k in headers:
                clean_trip[k] = v
        clean_trips.append(clean_trip)
    return pd.DataFrame(clean_trips)

def get_queue_timeseries(root: Element) -> dict:
    """
    Parses SUMO queue output file into a dictionary
    https://sumo.dlr.de/docs/Simulation/Output/QueueOutput.html
    """
    if root.tag != "queue-export":
        raise TypeError(
            F"Wrong input tag, {root.tag} was given but, <queue-export> expected.")

    result = {}
    for data in root:
        t = data.attrib["timestep"]
        for lane in data[0]:
            lane_id = lane.attrib["id"]
            if lane_id not in result.keys():
                result[lane_id] = {
                    "internal": False,
                    "t": [],
                    "queueing_time": [],
                    "queueing_length": []
                }
            
            if lane_id.startswith(":"):
                result[lane_id]["internal"] = True
            
            result[lane_id]["t"].append(t)
            for key in ["queueing_time", "queueing_length"]:
                result[lane_id][key].append(lane.attrib[key])
    return result

def get_detector_timeseries(root: Element, prefix="e2det_") -> dict:
    """
    Parses SUMO detector output file into a dictionary
    https://sumo.dlr.de/docs/Simulation/Output/Lanearea_Detectors_%28E2%29.html
    """      
    if root.tag != "detector":
        raise TypeError(
            F"Wrong input tag, {root.tag} was given but, <detector> expected.")

    METRICS = {
        "meanTimeLoss":"mean_time_loss",
        "meanSpeed": "mean_speed",
        "maxVehicleNumber": "count",
        "maxHaltingDuration": "max_waiting_time",
        "meanHaltingDuration": "mean_waiting_time",
        "maxJamLengthInVehicles": "max_queue_veh",
        "maxJamLengthInMeters": "max_queue_meters"
    } # where does it go to satisfy open/closed principle

    result = {}
    for interval in root:
        lane_id = interval.attrib["id"].split(prefix)[-1]
        t = interval.attrib["begin"]
        if lane_id not in result.keys():
            result[lane_id] = {
                "internal": False,
                "t": []}
            [result[lane_id].update({k: []}) for k in METRICS.keys()]
        
        if lane_id.startswith(":"):
            result[lane_id]["internal"] = True
            
        result[lane_id]["t"].append(t)
        for key in METRICS.keys():
            result[lane_id][key].append(interval.attrib[key])

    return result

def get_lanedata_timeseries(root: Element) -> dict:
    """
    Parses SUMO lane based emission output file into a dictionary
    https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Emissions_Measures.html
    """

    if root.tag != "meandata":
        raise TypeError(
            F"Wrong input tag, {root.tag} was given but, <meandata> expected.")

    METRICS = {
        "id": "lane",
        "traveltime": "travel_time",
        "fuel_perVeh": "fuel_per_veh",
        "C02_perVeh": "co2_per_veh",
        "C02_abs": "co2_abs",
        "C02_normed": "co2_per_kmh",
    }

    result = []
    for interval in root:
        begin = interval.attrib["begin"]
        end = interval.attrib["end"]
        for edge in interval:
            for lane in edge:
                entry = {"begin": begin, "end": end}
                metrics = {METRICS[k]: v for k, v in lane.attrib.items() if k in METRICS}
                entry.update(metrics)
                result.append(entry)

    return result
