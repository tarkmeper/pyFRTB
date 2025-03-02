import copy
import numpy
import operator

from FRTB.engine import Engine, schema_load
from FRTB.sba.subbucket import SubBucketEngine
from FRTB.sba.util import kb_sb_aggregator

_SCHEMA = schema_load("sba_variable.yaml")


class SBAVariableBucketEngine(Engine):
    """
    Variable bucket engine operates on an unknown # of buckets which are based on the actual input trades; risk
    factor such as FX/GIRR use this where while conceptually all currencies are known at the satart only used
    currencies are included and bucketed.

    The enigne operates on the level of a sensitivity type (FX-Vega) or (GIRR-curvature) with the underlying buckets
    being handled by a "sub_bucket_engine".  The sub_bucket_engine is responsible for the loweest level of bucketting
    in the calcualtion.
    """

    def __init__(self, hierarchy, sens_type, asset_class_details):
        # override any values in the root of this sensitivity type with specific values from this sensitivity
        # type.
        details = copy.copy(asset_class_details)
        details.update(asset_class_details[sens_type])

        super().__init__(f"{hierarchy}::{sens_type}", _SCHEMA, details)

        self.buckets = {}
        if 'added_bucket_fields' in details:
            self.bucket_fields = copy.copy(details['bucket_fields'])
            self.bucket_fields.update(details['added_bucket_fields'])
        else:
            self.bucket_fields = details["bucket_fields"]

        self.correlation = details["correlation"] / 100.0
        self.fields = details["fields"]
        self.sensitivity_type = sens_type
        self.RW = details["RW"]
        self.RW_lookup = lambda x: (self.RW[x] if x in self.RW else self.RW["default"])

    def add(self, sens_entry, weight=1.0):
        # for the variable buckets we assume that all variable buckets are just based on fields without any
        # co-ersion or corrections; if this changes in the future would need to adjust accordingly.
        bucket = operator.itemgetter(*self.fields)(sens_entry)
        if bucket not in self.buckets:
            self.buckets[bucket] = SubBucketEngine(self.hierarchy + "::" + bucket, self.bucket_fields)
        self.buckets[bucket].add(sens_entry, weight)

    def calculate(self, modifiers):
        num_buckets = len(self.buckets)

        # following helps with debugging, for test cases can set breakpoint after this to pick up the
        # actual calculations that are being applied.
        if num_buckets == 0:
            return {'total': 0.0}

        values = numpy.empty(num_buckets)
        sums = numpy.empty(num_buckets)
        rw = numpy.empty(num_buckets)

        for idx, (name, val) in enumerate(self.buckets.items()):
            sums[idx], values[idx] = val.calculate(modifiers)
            rw[idx] = self.RW_lookup(name)

        numpy.multiply(values, rw, out=values)
        numpy.multiply(sums, rw, out=sums)

        # correlation is much more complicated for vega - as we need to store all options
        correlation = numpy.minimum(1.0, self.correlation * modifiers["correlation-multiplier"])

        # handle the special case for curvature where the correlations and math are slightly adjusted.
        if self.sensitivity_type == "curvature":
            value = kb_sb_aggregator(values, sums, correlation ** 2, curvature_adjustment=True)
        else:
            value = kb_sb_aggregator(values, sums, correlation)

        return {"total": value}
