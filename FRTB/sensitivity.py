from FRTB.engine import Engine, schema_load

from FRTB.sba.variable_buckets import SBAVariableBucketEngine
from FRTB.sba.fixed_buckets import SBAFixedBucketEngine

SENSITIVITY_TYPES = ["delta", "vega", "curvature"]

_SCHEMA = schema_load("sba_root.yaml")


class SensitivityBasedApproach(Engine):
    """
    Sensitivty calculations are the most complex in FRTB with numerous different types of aggregation and calculations
    as much as posible this has been captured in configuration files to enable changes to exactly how the calculations
    are executed.

    At this level structure is fairly simple - a seperate engine is created for each asset class and sensitivity type
    with the only logic really being to determine that next level down uses "fixed" buckets (i.e. a pre-established
    list) or variable buckets (FX/GIRR) where the number of buckets can vary.
    """

    def __init__(self, cfg):
        """
        Setup an engine to calculate each of the asset class, risk type pair.

        There are two types of engines; for risk factors with predefined buckets (Commodity/Equity and Credit) we
        create a FixedBucket engine.  For risk factors that bucket based on currency we create a
        VariableBucket  engine which will dynamically create more buckets as needed.
        """
        super().__init__("sba", _SCHEMA, cfg)

        for asset_class, asset_cfg in cfg.items():
            for sens_type in SENSITIVITY_TYPES:

                match asset_cfg["mode"]:
                    case "fixed":
                        engine = SBAFixedBucketEngine(f"sba::{asset_class}", sens_type, asset_cfg)
                    case "variable":
                        engine = SBAVariableBucketEngine(f"sba::{asset_class}", sens_type, asset_cfg)
                    case _:
                        raise KeyError(f" {sens_type} on asset class {asset_class} unknown type {asset_cfg["type"]}")
                self.buckets[(asset_class, sens_type)] = engine

    def add(self, trade, weight):
        if "sensitivity" not in trade:
            raise KeyError(f"Missing sensitivity entry for trade {trade}")

        for entry in trade["sensitivity"]:
            asset_class = entry["class"]
            sens_type = entry["measure"]

            # Check if we need this sensitivity in this type of calculation if not we don't need to keep it
            if (asset_class, sens_type) not in self.buckets:
                continue

            self.buckets[(asset_class, sens_type)].add(entry, weight)

    def calculate(self, modifiers):
        """
        Calculation is largely delegated to the various engines to perform.  The total is just the sum of the
        results provided by the engines.
        """
        result = {}
        for key, engine in self.buckets.items():
            result[str(key)] = engine.calculate(modifiers)
        result["total"] = sum([x["total"] for x in result.values()])
        return result
