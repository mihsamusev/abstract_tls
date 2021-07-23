import argparse
import xml.etree.ElementTree as ET
from itertools import permutations

def get_transition_between(state_this, state_next, n_ped=0):
    """
    Calculates the transitions between this and next state using
    rules of each signal:
    - green -> green = green
    - green -> red = yellow
    - otherwise red
    """
    str_len = len(state_this)
    rgy_yellow = []

    for col_this, col_next in zip(state_this, state_next):
        if col_this.lower() == 'g' and col_next == 'r':
            rgy_yellow.append('y')
        elif col_this.lower() == 'g' and col_next.lower() == 'g':
            rgy_yellow.append(col_this)
        else:
            rgy_yellow.append('r')

    if n_ped > 0:
        rgy_ped = ["r" if col == 'y' else col for col in rgy_yellow[-n_ped:] ]
        rgy_yellow[-n_ped:] = rgy_ped

    out = "".join(rgy_yellow)
    return out

def get_phase_string(logic_ET, phaseID):
    """
    """
    for i, phase in enumerate(logic_ET.iter('phase')):
        if i == phaseID:
            return phase.get('state')
    else:
        return None

def add_phase_to_tree(logic_ET, id_from, id_to, state, duration=3):
    """
    Appends a phase to the xml tree of <tlLogic><\tlLogic> tag
    """
    logic_ET[-1].tail = "\n\t\t"
    child = ET.SubElement(logic_ET, "phase", attrib={
        "duration": str(duration),
        "state": state,
        "next": str(id_to),
        "name": f"({id_from}, {id_to})"
    })
    child.tail = "\n\t"


def generate_transition(logic_ET, id_from, id_to, duration=3, n_ped=4):
    """
    Generates the signal phase string to safely transition between id_from to id_to
    """
    state_this = get_phase_string(logic_ET, id_from)
    state_next = get_phase_string(logic_ET, id_to)
    id_yellow = get_transition_between(state_this, state_next, n_ped)
    add_phase_to_tree(logic_ET, id_from, id_to, id_yellow, duration)

def pairs(s):
    """
    (i_from, i_to) pairs mapped from argparse input
    """
    try:
        i_from, i_to = map(int, s.split(','))
        return i_from, i_to
    except:
        raise argparse.ArgumentTypeError("Coordinates must be from1,to1 from2,to2 ...")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--tls-program", required=True, help=
        "path to *.tll.xml file defining green / red only traffic light program")
    ap.add_argument("-o", "--output", required=True, help=
        "path to an output *.tll.xml file with new intermediate yellow phases")
    ap.add_argument("-e", "--exclude-pairs", type=pairs, default=[], nargs="+", help=
        "list of phase transitions to exclude: from1,to1 from2,to2 ...")
    ap.add_argument("-i", "--include-pairs", type=pairs, default=[], nargs="+", help=
        "list of phase transitions to exclude: from1,to1 from2,to2 ...")
    ap.add_argument("-p", "--pedestrian-lights", type=int, default=4, help=
        "number of pedestrian light signals in the signal state string")
    ap.add_argument("-y", "--yellow-duration", type=int, default=3, help=
        "duration of a yellow transition phase")
    args = ap.parse_args()

    # get xml tree
    tree = ET.parse(args.tls_program)
    root = tree.getroot()
    logic_ET = root[0]

    n_phases = len(logic_ET)

    if not args.include_pairs:
        args.include_pairs = permutations(range(n_phases), 2)
    
    last_unique = -1
    update_idx = 0
    for pair in args.include_pairs:
        if pair not in args.exclude_pairs:
            generate_transition(
                logic_ET,
                id_from=pair[0],
                id_to=pair[1],
                duration=args.yellow_duration,
                n_ped=args.pedestrian_lights
                )

            # update next of base phases to first transition
            
            if pair[0] != last_unique:
                logic_ET[update_idx].set('next', str(n_phases))
                update_idx += 1
                last_unique = pair[0]
            n_phases += 1

    tree.write(args.output)





