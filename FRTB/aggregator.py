"""
Engine are the main calculation component for the FRTB.
"""
import copy
import json
import numpy

from jsonschema import Draft202012Validator

from FRTB.residual import Residual
from FRTB.jtd import JTD
from FRTB.sensitivity import SensitivityBasedApproach
from FRTB.engine import schema_load

TRADE_SCHEMA = schema_load("trade.yaml")

COMPONENTS = {
    "sensitivity": SensitivityBasedApproach,
    "residual": Residual,
    "jtd": JTD,
}

DEFAULT_MODIFIERS = {
    "correlation-multiplier": 1.0
}


def init(config: dict) -> "Aggregator":
    """
    Initialize an empty calculation engine.

    :param config: Dictionary (or YAML file) with the configuration settings for this calculation.
    :return: An empty engine for performing calculations.
    """
    return Aggregator(config)


class Aggregator:
    """
    Core calculation object.

    Each engine is capable of maintaining an aggregation state with multiple trades; engines can be merged or serialized
    enabling calculations to occur in parallel.

    Serializing and copying engines enables calculations of marginal contributions by scaling at -1.
    """

    def __init__(self, cfg):
        """
        Initialize an aggregator with each of the components that are specified in the configuration
        file.

        Key detail here is the error variable which stores all the errors that have accumulated in the configuration
        file setup.
        """
        self.cfg = copy.deepcopy(cfg)
        self.components = {}

        for item, details in cfg.items():
            try:
                cls = COMPONENTS[item]
            except KeyError:
                raise KeyError("Unknown calculation component specified in input configuration: <%s>" % item)

            self.trade_validator = Draft202012Validator(TRADE_SCHEMA)
            self.components[item] = cls(details)

    def merge(self, other: "Aggregator", weight: float = 1.0) -> None:
        """
        Given two calculation engines, merge the input into this engine to produce a combined aggregation set.
        The engines must be configured in the same way.

        Note that the weight here is applied linearly to all objects.  Unlike the scale function which will adjust
        longs and shorts this does not and instead directly acts as if the final results are scaled.  Specifcially the
        following will produce differente behvaious:

            y = x.copy()
            y.scale(-1)
            z = x.merge(y, 1)

        and
            y = x.copy()
            z = x.merge(y, -1)

        In the second case the result is guaranteed to be zero; in the first case for risk components where longs and
        shorts are treated differently those will not cancel out since the scale function will not know to adjust
        and cancel that exposure.

        :return: Updated engine with the items now merged in.
        """
        # This is pretty hacky - but I think will work; we want to check the two configuration files to make sure they
        # are identical.  This does this automatically recursively which makes it convinient.
        if json.dumps(self.cfg, sort_keys=True) != json.dumps(other.cfg, sort_keys=True):
            raise RuntimeError("Configurations do not match")

        # since init always initializes all components we can assume component must exist in both.
        for key, value in self.components.items():
            assert key in other.components
            value.merge(other.components[key], weight)
        return self

    def add(self, trade: dict, weight: float = 1.0) -> None:
        """
        Update internal aggregations to include a new trade in this engine.

        :param trade: The trade to append.
        :param weight: The weight to apply to this set of trades, multiples values basd on the weight.
        """
        errors = sorted(self.trade_validator.iter_errors(trade), key=lambda e: e.path)
        if errors:
            raise ExceptionGroup('Trade is in valid with the following errors', errors)

        # we want to make sure if for any reason a trade fails to add remvoe it so that the system is in a consistent
        # state of the system.  This way if a trade fails it is not "partially" added to the calculation and can either
        # safely be retried or be skipped.
        completed = []
        try:
            for component in self.components.values():
                component.add(trade, weight)
                completed += [component]
        except Exception as e:
            for component in completed:
                component.add(trade, -1 * weight)
            raise e

    def scale(self, weight: float = 1.0) -> None:
        """
        Increase or decrease the size of the passed in partial by the given scale.  This does not just scale the results
        but conceptually adjusts longs and shorts appropriately to ensure the calculation is as if every trade inside
        the aggregator had been increased by the weight passed in.

        In specific in certain calculations where longs and shorts do not directly cancel this results in the
        appropriate action being taken on the scaled object.
        """
        for val in self.components.values():
            val.scale(weight)

    def calculate(self, modifiers: dict[str, float] = None) -> dict:
        """
        Create a results dictionary that has both the overall results and numerous partial results from all the stages
        of the calcualtion.

        :param modifiers: Modifiers to the calculation, these can be used to provide additional configurations to the
        calculation
        :return:  Result dictionary. "total" key provides final result with number of breakdowns within the calculation.
        """
        final_modifiers = copy.deepcopy(DEFAULT_MODIFIERS)
        if modifiers is not None:
            final_modifiers.update(modifiers)

        result = {}
        for key, value in self.components.items():
            result[key] = value.calculate(final_modifiers)
            assert "total" in result[key]  # assumed that each component will produce a total result for the overall.

        result["total"] = sum([f["total"] for f in result.values()])
        return result

    def json_dump(self):
        """
        Dump an internal representation of all the various calculations in JSON format, useful for debugging
        purposes.

        To save and restore copies use file pickle instead.
        """
        res = {}
        for key, value in self.components.items():
            res[key] = value.to_json()
        return json.dumps(res, cls=NumpyEncoder)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
