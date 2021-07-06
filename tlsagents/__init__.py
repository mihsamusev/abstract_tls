import os
import glob
import importlib

# import entire content of the agents folder / package in order
# to activate the factory registration

dir_path = os.path.dirname(__file__)
dir_name = os.path.basename(dir_path)

module_paths = glob.glob(
    os.path.join(dir_path, "*.py"))

for p in module_paths:
    if os.path.isfile(p) and not os.path.basename(p).startswith('_'):
        module_name = os.path.basename(p).replace(".py", "")
        importlib.import_module(f"{dir_name}.{module_name}")

