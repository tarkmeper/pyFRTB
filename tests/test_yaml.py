"""
    Test to verify that package YAML files are valid and not empty.
"""
import glob
import os.path as path

import pytest
import yaml

file_list = glob.glob(path.join(path.dirname(__file__), "../FRTB/cfg/*.yaml"))


@pytest.mark.parametrize("f", file_list)
def test_yaml(f):
    yaml_file = yaml.load(open(f, "r"))
    assert yaml_file is not None
