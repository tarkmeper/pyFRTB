import importlib_resources
import yaml

from FRTB.aggregator import init


def _cfg_load(name):
    return open(importlib_resources.files("FRTB") / "cfg" / name)


D352_1 = {
    "sensitivity": yaml.load(_cfg_load('d352_jan2016_sba.yaml'), yaml.SafeLoader),
    "residual": yaml.load(_cfg_load('d352_jan2016_residual.yaml'), yaml.SafeLoader),
    "jtd": yaml.load(_cfg_load('d352_jan2016_jtd.yaml'), yaml.SafeLoader)
}
