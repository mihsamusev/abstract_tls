import argparse
import pathlib
import os
import shutil
import confuse
import json


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


class AllowedContainers(confuse.templates.TypeTemplate):
    def __init__(self, typ):
        super().__init__(typ)

    def __repr__(self):
        return repr(self.typ)


def get_valid_config(args):
    """
    Get a config dict for CLI and valdate all parameters
    """
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
        }
    }
    job_config = config.get(job_template)

    logging_template = confuse.Optional(
            confuse.MappingTemplate({
                'ids': confuse.StrSeq(),
                'data': confuse.Sequence(
                   confuse.Choice(['objectives', 'state', 'variables'])),
                'timestamped': confuse.Optional(bool, default=True),
                "to_file": confuse.Optional(bool, default=True),
                "to_console": confuse.Optional(bool, default=False)
            })
        )

    sumo_template = {
        "dir": FilenameValidate(
            cwd=job_config.job.dir),
        "gui": confuse.Optional(bool, default=True),
        "max_steps": confuse.Optional(int, default=10e5),
        "network": FilenameValidate(relative_to="dir"),
    }
    sumo_config = config.get({"sumo": sumo_template})
    sumo_template["additional"] = confuse.Sequence(
            FilenameValidate(cwd=sumo_config.sumo.dir))
    sumo_template["route"] = confuse.Sequence(
            FilenameValidate(cwd=sumo_config.sumo.dir))

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
        "extract": {
            "user_data": confuse.Sequence({
                "feature": confuse.Choice(
                    ["count", "speed", "eta", "delay", "waiting_time"]),
                "user_class": confuse.Choice(
                    ["bicycle", "passenger", "pedestrian", "bus", "truck", "moped"]),
                "at": confuse.Choice(
                    ["lane", "detector", "phase"]),
                "mapping": AllowedContainers(dict)
                }),
            "tls_data": confuse.Sequence({
                "feature": confuse.Choice(
                    ["elapsed_time", "integer_phase", "binary_phase"]),
                "to_variable": str
            })
        }
    })

    full_template = {
        "logging": logging_template,
        "sumo": sumo_template,
        "tls": tls_template,
    }
    job_template.update(full_template)
    valid_config = config.get(job_template)

    # second round of sumo validation
    assert len(valid_config.sumo.route) > 0, \
        "No demand definition: sumo.route is an empty list, expected at least one *.rou.xml"
    
    # second round of logger validation, look if ids are given
    if valid_config.logging:
        if valid_config.logging.ids and valid_config.logging.data:
            output_dir = os.path.join(valid_config.job.dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            valid_config.logging.update({"dir": output_dir})
        else:
            del valid_config['logging']

    return valid_config

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", type=str, required=True,
        help="yaml configuration file")
    args = ap.parse_args()
    cfg = get_valid_config(args)
    print(json.dumps(cfg, indent=4))