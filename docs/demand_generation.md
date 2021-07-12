## Demand generation

Demand is generated using `randomTrips.py`

For vehicles - binomial with `n = 5` and `p = peirod / 5 = 1/5`

```sh
python $SUMO_HOME/tools/randomTrips.py \
    -n data/block.net.xml \
    --weights-prefix data/edge_weights \
    -o data/vehicles.rou.xml \
    --seed 42 \
    --validate \
    -b 0 \
    -e 3000 \
    --binomial 5
```

For pedestrians - uniform every 5s
```sh
python $SUMO_HOME/tools/randomTrips.py \
    -n data/block.net.xml \
    -o data/pedestrians.rou.xml \
    --pedestrians \
    --max-distance 100 \
    --period 5 
```