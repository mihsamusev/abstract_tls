# Generate template file for the detectors

```sh
python $SUMO_HOME/tools/output/generateTLSE2Detectors.py \
    -n examples/cross/sumo/networks/cross6_LFR_exits.net.xml \
    -o examples/cross/sumo/det/radars.det.xml \
    -r ../../output/detectors.xml 
```