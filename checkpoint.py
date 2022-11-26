import os
import json


class Checkpoint:
    def __init__(self, cpt_dir, basename, instrnum, weight, gzname=""):
        self.cpt_dir = cpt_dir
        self.basename = basename
        self.instrnum = instrnum
        self.weight = weight
        self.gzname = gzname

    def get_dir(self):
        sub_dir = self.basename + "_" + self.instrnum + "_" + str(self.weight)
        return os.path.join(self.cpt_dir, sub_dir, "0")

    def get_path(self):
        return os.path.join(self.get_dir(), self.gzname)

    def output_dir(self, prefix=""):
        return os.path.join(prefix, self.basename + "_" + self.instrnum + "_" + self.weight)

    def __str__(self):
        return self.get_path()


def get_cpt_config(checkpoint_dir, config_json_path=None):
    if config_json_path is None:
        config_json_path = os.path.join(checkpoint_dir, "json/simpoint_summary.json")
    with open(config_json_path) as f:
        cpt_config = json.load(f)
    return cpt_config


def get_checkpoints(checkpoint_dir, config_json_path=None):
    cpt_config = get_cpt_config(checkpoint_dir, config_json_path)
    checkpoints = []
    for bmk, bmk_config in cpt_config.items():
        for instnum, weight in bmk_config.items():
            cpt = Checkpoint(os.path.join(checkpoint_dir, "take_cpt/"), bmk, instnum, weight)
            cpt_dir = cpt.get_dir()
            files = os.listdir(cpt_dir)
            assert len(files) == 1
            cpt.gzname = files[0]
            checkpoints.append(cpt)
    return checkpoints


if __name__ == '__main__':
    cpts = get_checkpoints("/nfs-nvme/home/share/checkpoints_profiles/spec06_rv64gcb_o2_20m")
    for c in cpts:
        print(c.output_dir())

