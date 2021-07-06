import argparse
import pathlib
import os
import shutil
import confuse
import json

from confuse.templates import TypeTemplate

from tlsagents.base import TLSFactory


class FilenameValidate(confuse.Filename):
    """
    Extend confuse.Filename to check existence of files and folders
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'Filename relative to {self.cwd}'

    def value(self, view, template=None):
        path = super().value(view, template)
        if os.path.exists(path):
            return path
        else:
            self.fail(f"No such file or directory: {path}", view, True)


class ExecutableValidate(confuse.Template):
    """
    Check existence of executables using "which" command
    """
    def __repr__(self):
        return f'Executable()'

    def value(self, view, template=None):
        path = view.get()
        abs_path = shutil.which(path)
        if abs_path is not None:
            return path
        else:
            self.fail(f"No such executable: {path}", view, True)


class AllowedContainers(TypeTemplate):
    def __init__(self, typ):
        super().__init__(typ)

    def __repr__(self):
        return repr(self.typ)


def get_valid_config():
    """
    Get a config dict for CLI and valdate all parameters
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", type=str, required=True,
        help="yaml configuration file")
    args = ap.parse_args()

    source = confuse.YamlSource(args.config)
    config = confuse.RootView([source])

    job_template = {
        "job": {
            "name": str,
            "dir": confuse.Optional(
                FilenameValidate(
                    cwd=str(pathlib.Path(__file__).parent.absolute())),
                    default=str(pathlib.Path(__file__).parent.absolute())
            ),
            "max_steps": 10e5,
            "logging": bool     
        }
    }
    job_config = config.get(job_template)

    sumo_template = {
        "dir": FilenameValidate(
            cwd=job_config.job.dir),
        "sumocfg": FilenameValidate(relative_to="dir"),
        "gui": True,
    }

    tls_template = confuse.Sequence({
            "id": str,
            "controller": confuse.Choice(
                TLSFactory.get_registered_keys()),
            "constants": confuse.MappingValues(
                confuse.OneOf([
                    confuse.Number(),
                    AllowedContainers(list),
                    AllowedContainers(dict),
                    FilenameValidate(cwd=job_config.job.dir),
                    ExecutableValidate()
                ])
            ),
            "variables": confuse.MappingValues(
                confuse.OneOf([
                    confuse.Number(),
                    AllowedContainers(list)
                ])
            ),
            "extract": confuse.Sequence({
                "user_class": confuse.Choice(
                    ["bicycle", "passenger", "pedestrian", "bus", "truck", "moped"]),
                "feature": confuse.Choice(
                    ["count", "speed", "eta", "delay", "waiting_time"]),
                "from": confuse.Choice(
                    ["lane", "detector", "phase"]),
                "mapping": AllowedContainers(dict)
            })
        })

    full_template = {
        "sumo": sumo_template,
        "tls": tls_template,
    }
    full_template.update(job_template)
    valid_config = config.get(full_template)

    return valid_config

if __name__ == "__main__":
    cfg = get_valid_config()
    print(json.dumps(cfg, indent=4))