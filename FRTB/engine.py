from abc import ABCMeta, abstractmethod
from copy import deepcopy
from jsonschema import Draft202012Validator, validate

import yaml
import importlib_resources


def schema_load(filename):
    schema = yaml.load(open(importlib_resources.files("FRTB") / "schema" / filename), yaml.SafeLoader)

    meta = Draft202012Validator.META_SCHEMA
    validate(schema, meta)
    return schema


class Engine(metaclass=ABCMeta):
    """
    Base engines class providing useful utilities for all the engines and a structure for the calculation tree that
    is generated.
    """

    def __init__(self, hierarchy, schema, details):
        self.buckets = {}
        self.hierarchy = hierarchy

        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(details), key=lambda e: e.path)
        if errors:
            raise ExceptionGroup(f'Component schema for {hierarchy} is not valid with the following errors', errors)

    @abstractmethod
    def add(self, trade, weight) -> None:
        pass

    @abstractmethod
    def calculate(self, _modifier) -> dict:
        pass

    def scale(self, weight) -> None:
        """
        Scale all buckets by the fixed weights.  See aggregator.py for more details.
        """
        for idx, val in self.buckets.items():
            if isinstance(val, float):
                self.buckets[idx] *= weight
            else:
                self.buckets[idx].scale(weight)

    def merge(self, other, weight) -> None:
        for idx, val in other.buckets.items():
            if idx not in self.buckets:
                self.buckets[idx] = deepcopy(val)
                self.buckets[idx].scale(weight)
            elif isinstance(val, float):
                self.buckets[idx] += val * weight
            else:
                self.buckets[idx].merge(val, weight)

    def to_json(self) -> dict:
        """
        Recursive printer of JSON debug details through all the sub-engines.  to reduce clutter and make it more
        readable empty engines are not returned.
        :return:
        """
        res = {}
        for idx, val in self.buckets.items():
            key = str(idx)
            if isinstance(val, Engine):
                json_val = val.to_json()
            else:
                json_val = val

            if json_val:
                res[key] = json_val
        return res
