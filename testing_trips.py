from metrics import tripinfostats as tis
import xml.etree.ElementTree as ET
root = ET.parse("test/data/metrics/tripinfo_with_emit.xml").getroot()

#df1 = tis.pedinfo_to_pandas(root)
#df2 = tis.tripinfo_to_pandas(root)

root = ET.parse("examples/cross/output/cross_queues.xml").getroot()
#print(tis.get_queue_timeseries(root)["EC_4"])


import pandas as pd

METRICS = {
    "begin": "begin",
    "end": "end",
    "id": "det_id",
    "meanTimeLoss":"mean_time_loss",
    "meanSpeed": "mean_speed",
    "maxVehicleNumber": "count",
    "maxHaltingDuration": "max_waiting_time",
    "meanHaltingDuration": "mean_waiting_time",
    "maxJamLengthInVehicles": "max_queue_veh",
    "maxJamLengthInMeters": "max_queue_meters"
}


### ADD LANE DATA
id_prefix = "e2det_"
df = pd.read_xml("examples/cross/output/cross_detectors.xml")
df = df[METRICS.keys()]
df.insert(3, "lane", df["id"].apply(lambda x: x.split(id_prefix)[-1]))

### ADD STREAM DATA
stream_map = {
    "EW_cars": ["EC_2", "EC_3", "EC_4", "WC_2", "WC_3", "WC_4"],
    "NS_cars": ["NC_2", "NC_3", "NC_4", "SC_2", "SC_3", "SC_4"],
    "EW_cyclist": ["EC_1", "WC_1"],
    "NS_cyclist": ["NC_1", "SC_1"]
}

def assign_stream(lane, stream_map):
    for stream, lanes in stream_map.items():
        if lane in lanes:
            return stream

    return None

df.insert(4, "stream", df["lane"].apply(assign_stream, args=[stream_map]))

df = df.rename(columns=METRICS)
print(df.head())

### ADD CO2 DATA
df = pd.read_xml("examples/cross/output/cross_detectors2.xml")
print(df.head())