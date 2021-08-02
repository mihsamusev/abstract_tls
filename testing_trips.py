from metrics import tripinfostats as tis
import xml.etree.ElementTree as ET
root = ET.parse("test/data/metrics/tripinfo_with_emit.xml").getroot()

df1 = tis.pedinfo_to_pandas(root)
df2 = tis.tripinfo_to_pandas(root)
print(df2)