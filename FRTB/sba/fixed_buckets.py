"""
Fixed bucket engines are used for cases where the list of values is known ahead of time.

This is primarily for factors like IR where the list of buckets overall is known ahead of time and
can so matrix can be pre-computed.
"""
import copy
import numpy
import operator
import itertools

from FRTB.engine import Engine, schema_load
from FRTB.sba.subbucket import SubBucketEngine
from FRTB.sba.util import kb_sb_aggregator, get_cross_correlation

_SCHEMA = schema_load("sba_fixed.yaml")


class SBAFixedBucketEngine(Engine):
    """
    FixedBucketEngines map all sensitivity to a set of fixed buckets (and an other bucket)
    for those that don't match.

    They create buckets which then aggregate all the sensitivities within that bucket.

    This assumes that the inputs have been run through JSON validation and generally valid, there are some additional
    checks here to caputre more complex validations that are hard to express in JSON.

    :param bucket_details: A map containing the details of this bucket
           must include "fields" indicating fields used for bucketting and
           "values" indicating the valid value range.
    :return: a function mapping a trade to a specified bucket
    """

    def __init__(self, hierarchy, sens_type, asset_class_details):
        # override any values in the root of this sensitivity type with specific values from this sensitivity
        # type.
        details = copy.copy(asset_class_details)
        details.update(asset_class_details[sens_type])

        super().__init__(f"{hierarchy}::{sens_type}", _SCHEMA, details)
        self.sensitivity_type = sens_type

        values = details["values"]

        if 'added_bucket_fields' in details:
            bucket_fields = copy.copy(details['bucket_fields'])
            bucket_fields.update(details['added_bucket_fields'])
        else:
            bucket_fields = details["bucket_fields"]


        corr = details["correlation"]
        fields = details["fields"]
        RW = copy.copy(details["RW"])
        other_treatment = details["other_treatment"]

        ## apply defaults
        if "default" in RW:
            for name in values:
                if name not in RW:
                    RW[name] = RW["default"]
            del RW["default"]

        if set(RW.keys()) - set(values.keys()) != set(['other']):
            delta = set(RW.keys()) - set(values.keys())
            raise ValueError(f"Riskweights and values in  {self.hierarchy} do not match.  Difference is {delta}")

        self.fields = fields
        self.RW = RW
        self.other_treatment = other_treatment
        self.bucket_name_to_idx, self.field_to_idx = _get_value_map(values)

        if isinstance(corr, dict):
            self.correlation = get_cross_correlation(corr, self.bucket_name_to_idx)
        else:
            self.correlation = corr

        for name, idx in self.bucket_name_to_idx.items():
            corr_override = None
            if 'internal_correlation' in details:
                corr_override = details['internal_correlation'][name]
            sub_name = f"{self.hierarchy}::{name}"
            self.buckets[idx] = SubBucketEngine(sub_name, bucket_fields, correlation_overide=corr_override)

        self.other_bucket = SubBucketEngine(f"{self.hierarchy}::other", bucket_fields, correlation_overide=0)

    def merge(self, other, weight):
        super().merge(other, weight)
        self.other_bucket.merge(other.other_bucket, weight)

    def scale(self, weight):
        super().scale(weight)
        self.other_bucket.scale(weight)

    def add(self, sens, weight=1.0):
        buckets = operator.itemgetter(*self.fields)(sens)
        try:
            idx = self.field_to_idx[buckets]
            self.buckets[idx].add_sensitivity(sens, weight)
        except KeyError:
            self.other_bucket.add(sens, weight)

    def calculate(self, modifiers):
        """
        Aggregate all sub-buckets, and then add the other bucket to the list.
        """
        length = len(self.buckets)
        values = numpy.empty((length,))
        sums = numpy.empty((length,))
        rw_vect = numpy.empty((length,))

        for name, idx in self.bucket_name_to_idx.items():
            try:
                rw_vect[idx] = self.RW[name]
            except KeyError:
                rw_vect[idx] = self.RW["default"]

        for idx in range(length):
            sums[idx], values[idx] = self.buckets[idx].calculate(modifiers)

        sums = numpy.multiply(sums, rw_vect)
        values = numpy.multiply(values, rw_vect)
        correlation = numpy.minimum(self.correlation * modifiers["correlation-multiplier"], 1.0)

        # deal with the other bucket
        add_on = 0
        if self.other_treatment == "flat_sum":
            add_on = self.other_bucket.abssum() * self.RW["other"]

        if self.sensitivity_type == "curvature":
            value = kb_sb_aggregator(values, sums, correlation ** 2, curvature_adjustment=True)
        else:
            value = kb_sb_aggregator(values, sums, correlation)

        return {"total": value + add_on}


def _get_value_map(values):
    """
    Return a mapping of the various combinations of values to the appropriate bucket.
    :param values: List of value lists.
    :return: map of
    """
    fields_to_idx = {}
    bucket_name_to_idx = {}
    for idx, (entry, vals) in enumerate(values.items()):
        bucket_name_to_idx[entry] = idx
        fields_to_idx.update({val: idx for val in itertools.product(*vals)})

    return bucket_name_to_idx, fields_to_idx
