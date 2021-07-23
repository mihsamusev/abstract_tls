import argparse
import xml.etree.ElementTree as ET

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--tls-program", required=True, help=
        "path to *.tll.xml file defining green / red only traffic light program")
    ap.add_argument("-n", "--number", type=int, help=
        "number of phases to account for")
    ap.add_argument("-p", "--pedestrian-lights", type=int, default=4, help=
        "number of pedestrian light signals in the signal state string")
    ap.add_argument("-d", "--decimal", dest='decimal', default=False, action='store_true', help=
        "Whether to output decimal instead of binary")
    ap.add_argument("-b", "--base", type=int, default=16, help=
        "base for the binary output")
    args = ap.parse_args()

    # get xml tree
    tree = ET.parse(args.tls_program)
    root = tree.getroot()
    logic_ET = root[0]
    
    if args.number is None:
        args.number = len(logic_ET)
    
    n_ped = args.pedestrian_lights
    for elem in logic_ET[:args.number]:
        bin_phase = ["1" if e.lower() == "g" else "0" for e in elem.get("state")]
        bin_phase = "".join(bin_phase)
        if n_ped > 0:
            bin_phase = bin_phase[:-n_ped]

        if len(bin_phase) < args.base:
            out = bin_phase.zfill(args.base)
        else:
            out = bin_phase[:args.base]   
        
        if args.decimal:
            out = str(int(out, 2))

        print(out)