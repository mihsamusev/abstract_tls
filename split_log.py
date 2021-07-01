import ast


def read_log(logfile):
    """
    Reads log line by line, converts strings to dicts and
    appends them to list
    """
    output = []
    with open(logfile, "r") as fin:
        for line in fin.readlines():
            output.append(ast.literal_eval(line))
    return output

def split_loglist(data, final_duration=100):
    """
    Splits the log into a dictionary wher keys are tls_id
    {"tls_id": [{"phase": int, "time": int}, {}, ... , {}], ...}
    """
    output = {}
    prev_time = {}
    for line in data:
        tls_id = line["states"]["id"]
        tls_phase = line["states"]["phase"]
        elapsed = line["states"]["elapsed"]
        if elapsed > 0:
            prev_time[tls_id] = elapsed

        # initialize
        if tls_id not in output:
            output[tls_id] = [{"phase": tls_phase, "duration": -1}]

        # append
        elif tls_phase != output[tls_id][-1]["phase"]:
            # update previous time
            output[tls_id][-1]["duration"] = prev_time[tls_id]
            output[tls_id].append(
                {"phase": tls_phase, "duration": -1})

    # fix last
    for val in output.values():
        if val[-1]["duration"] == -1:
            val[-1]["duration"] = final_duration
          
    return output

def get_tls_dicts(logfile):
    """
    get tls sequences from logfile
    """
    loglist = read_log(logfile)
    splits = split_loglist(loglist)
    return splits 


if __name__ == "__main__":
    import json
    import sys
    logfile = sys.argv[-1]
    splits = get_tls_dicts(logfile)
    
    with open("results.txt", "w") as fout:
        json.dump(splits, fout, indent=4)