
import os
import argparse
import xml.etree.ElementTree as ET
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

def get_detector_intervals(root: Element, prefix="e2det_") -> list:
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

    result = []
    for interval in root:
        lane_id = interval.attrib["id"].split(prefix)[-1]
        begin = interval.attrib["begin"]
        end = interval.attrib["end"]
        entry = {
            "begin": float(begin),
            "end": float(end),
            "lane": lane_id
        }
        metrics = {METRICS[k]: float(v) for k, v in interval.attrib.items() if k in METRICS}
        entry.update(metrics)
        result.append(entry)
    return result

def get_emission_intervals(root: Element) -> list:
    """
    Parses SUMO lane based emission output file into a dictionary
    https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Emissions_Measures.html
    """

    if root.tag != "meandata":
        raise TypeError(
            F"Wrong input tag, {root.tag} was given but, <meandata> expected.")

    METRICS = {
        "traveltime": "travel_time",
        "fuel_perVeh": "fuel_per_veh",
        "CO2_perVeh": "co2_per_veh",
        "CO2_abs": "co2_abs",
        "CO2_normed": "co2_per_kmh",
    }

    result = []
    for interval in root:
        begin = interval.attrib["begin"]
        end = interval.attrib["end"]
        for edge in interval:
            for lane in edge:
                entry = {
                    "begin": float(begin),
                    "end": float(end),
                    "lane": lane.attrib["id"]
                }
                metrics = {METRICS[k]: float(v) for k, v in lane.attrib.items() if k in METRICS}
                missing_metrics = {m: 0.00 for m in METRICS.values() if m not in metrics}
                entry.update(metrics)
                entry.update(missing_metrics)
                result.append(entry)

    return result

def assign_stream(lane, stream_map):
    """
    Finds a stream of a lane based on the dictionary
    """
    for stream, lanes in stream_map.items():
        if lane in lanes:
            return stream

    return None

def search_folder(path: str, extensions: dict, prefix_sep="_") -> dict: 
    """
    Creates a dictionary with output with fienames belonging to
    the same run.
    """
    runs = {}
    for filename in os.listdir(path):
        run_name = filename.split(prefix_sep)[0]
        if run_name not in runs:
            runs[run_name] = {k: "" for k in extensions.keys()}
        
        for key, pattern in extensions.items():
            if filename.endswith(pattern):
                runs[run_name][key] = os.path.join(path, filename)
    return runs


def read_detectors_to_pandas(file: str) -> pd.DataFrame:
    root = ET.parse(file).getroot()
    dct = get_detector_intervals(root)
    return pd.DataFrame(dct)

def read_emissions_to_pandas(file: str) -> pd.DataFrame:
    root = ET.parse(file).getroot()
    dct = get_emission_intervals(root)
    return pd.DataFrame(dct)

def merge_detectors_and_emissions(det: pd.DataFrame, emit: pd.DataFrame) -> pd.DataFrame:
    """
    Merges data frames coming from detectors and emissions output files
    """
    return pd.merge(det, emit, how="inner", on=["begin", "end", "lane"])

def add_lane_group_column(df: pd.DataFrame, group_map: dict) -> pd.DataFrame:
    """
    Adds a stream column based on the dictionary
    """
    df.insert(0, "lane_group", df["lane"].apply(
        assign_stream, args=[group_map]))
    return df

def output_folder_to_pandas(output_dir: str) -> pd.DataFrame:
    """
    Combine all contents of the output folder to a single DataFrame.
    """
    runs = search_folder(
        output_dir,
        extensions={"det": "det.xml", "emit": "emit.xml"}
    )

    dfs = []
    for run_name, run_files in runs.items():
        df_det = read_detectors_to_pandas(run_files["det"])
        df_emit = read_emissions_to_pandas(run_files["emit"])
        df = merge_detectors_and_emissions(df_det, df_emit)
        df.insert(0, "run_name", run_name)
        dfs.append(df)
    
    return pd.concat(dfs, axis=0)
    

if __name__ == "__main__":
    ag = argparse.ArgumentParser()
    ag.add_argument("-f", "--folder", type=str, required=True, help=
        "Path to the folder with detector and lane emissions output")
    args = ag.parse_args()

    df = output_folder_to_pandas(args.folder)
    group_map = {
        "EW_cars": ["EC_2", "EC_3", "EC_4", "WC_2", "WC_3", "WC_4"],
        "NS_cars": ["NC_2", "NC_3", "NC_4", "SC_2", "SC_3", "SC_4"],
        "EW_cyclist": ["EC_1", "WC_1"],
        "NS_cyclist": ["NC_1", "SC_1"]
    }
    df = add_lane_group_column(df, group_map)
    print(df.head())
