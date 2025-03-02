import operator

import numpy
import math

from collections import namedtuple

from FRTB.engine import Engine, schema_load
from FRTB.sba.util import get_cross_correlation

FieldDetails = namedtuple("FieldDetails", ["name", "grouping", "mapping", "rw_multiplier", "correlation"])

_SCHEMA = schema_load("sba_subbucket.yaml")


class SubBucketEngine(Engine):
    """
    This is likely the most complex of the engines supporting grouping below the bucket level and computing dedicated
    RW and correlations for the curves in these buckets.

    The bucket_fields object in the configuration files are expected to be alist of field names with the following
    properties:
        *  grouping - value [ each value is seperate ]; tenor [ grouped into specified tenor buckets ]
        *  Correlation -
                - for value entries this should just be a constant value
                - for tenor this should be the theta and floor for the calculation
        * RW_multiplier: multiplier for RW adjustments.  This behavesw  the same way as the top-level RW in the
          sensitivity type calculations.
    """

    def __init__(self, hierarchy, bucketting_fields, correlation_overide=None):
        """
        A lot of this data could be calculated and stored at the parent level; however, doing this makes the code
        harder to read and manage.  Given that the number of buckets is usually relatively small (50-100) redoing this
        calculation repeatedly isn't likely to be an issue.

        :param details: The bucket_fields details list
        """
        super().__init__(hierarchy, _SCHEMA, bucketting_fields)

        # Other fields
        self.correlation_overide = correlation_overide
        self.fields = []
        self.field_details = []

        for field_name, details in sorted(bucketting_fields.items()):
            grouping = details["grouping"]

            if grouping == "value":
                rw_multiplier = details["RW_multiplier"] if "RW_multiplier" in details else 1.0
                correlation = details["correlation"] / 100.0
                mapping = None
            elif grouping == 'tenor-value':
                rw_multiplier = details["RW_multiplier"] if "RW_multiplier" in details else 1.0
                correlation = details["correlation"]
                mapping = None
            elif grouping in ["bins", "tenor"]:
                values = details["values"]
                rw_tmp = details["RW_multiplier"] if "RW_multiplier" in details else None

                if grouping == "bins":
                    corr_type = details["correlation"]["type"]
                    corr_tmp = details["correlation"]
                else:
                    corr_tmp = details["correlation"]
                    corr_type = "tenor"

                mapping, rw_multiplier, correlation = _init_bins(values, rw_tmp, corr_type, corr_tmp)
            else:
                raise ValueError(f"Invalid grouping type {val['grouping']}")

            part = FieldDetails(field_name, grouping, mapping, rw_multiplier, correlation)
            self.fields.append(field_name)
            self.field_details.append(part)

    def _adjust_bucket(self, bucket_raw):
        """
        Adjust the bucket based on the field details; this is used to convert the trade into a bucket.
        The way we adjust the buckets depends on the type for each field
        """
        assert len(bucket_raw) == len(self.field_details)
        bucket_data = []
        for value, details in zip(bucket_raw, self.field_details):
            match details.grouping:
                case "value" | "tenor-value":
                    bucket_data.append(value)
                case "bins" | "tenor":
                    bucket_data.append(details.mapping[value])
                case _:
                    raise ValueError(f"Invalid grouping type {details.grouping}")
        return tuple(bucket_data)

    def add(self, sens_entry, weight):
        bucket_raw = operator.itemgetter(*self.fields)(sens_entry)
        if len(self.fields) == 1:
            bucket_raw = (bucket_raw,)
        bucket = self._adjust_bucket(bucket_raw)

        if bucket not in self.buckets:
            self.buckets[bucket] = 0
        self.buckets[bucket] += sens_entry["value"] * weight

    def abssum(self):
        return sum(map(abs, self.buckets.values()))

    def calculate(self, _modifiers):
        """
        Returns the correlation adjsuted value; using the buckets to value
        based on the correlation matrix.
        """
        if len(self.buckets) == 0:
            return 0.0, 0.0

        values = numpy.array(list(self.buckets.values()))
        matrix = numpy.ones((len(values), len(values)))

        # can't use numpy to transpose as there could be different types - if this becomes performance critical could
        # instead map the elements to index #s and then transpose.
        keys_list = list(self.buckets.keys())
        keys_transpose = list(map(list, zip(*keys_list)))

        for field, keys in zip(self.field_details, keys_transpose):
            keys_arr = numpy.array(keys)
            match field.grouping:
                case "value":
                    rw_vect, corr = _calculate_value_grouping(keys_arr, field)
                    rw_vect = field.rw_multiplier
                case "tenor-value":
                    corr = _vega_tenor_correlation_calc(keys_arr, field.correlation["theta"] / 100)
                    rw_vect = field.rw_multiplier
                case "bins" | "tenor":
                    corr, rw_vect = _calculate_bins_grouping(keys_arr, field)
                case _:
                    assert False

            matrix *= corr
            values *= rw_vect
        rw_values = values[:, None] * values  # create a 2-d correlation matrix
        final = numpy.multiply(rw_values, matrix)
        return values.sum(), math.sqrt(final.sum())


def _vega_tenor_correlation_calc(tenors, factor, minimum=-1.0, maximum=1.0):
    """
    The volatility correlation is described in section 125; this computes
    all the pair-wise correlations for a single set of tenors.

    :param tenors: numpy array of tenors.  These can be in any order.
    """
    numerator = numpy.abs(tenors[:, None] - tenors)
    denominator = numpy.minimum(tenors[:, None], tenors)
    exponent = numpy.exp(factor * numerator / denominator)
    correlation_factor = numpy.maximum(numpy.minimum(exponent, maximum), minimum)
    numpy.fill_diagonal(correlation_factor, 1.0)
    return correlation_factor


def _init_bins(values, rw_tmp, correlation_type, corr_tmp):
    mapping = {item: idx for idx, item in enumerate(values)}
    mapping[None] = -1

    if correlation_type == "flat":
        correlation = numpy.zeros([len(values), ] * 2)
        correlation.fill(corr_tmp["value"] / 100.0)
        numpy.fill_diagonal(correlation, 1.0)
    elif correlation_type == "matrix":
        correlation = get_cross_correlation(corr_tmp["matrix"], mapping)
    elif correlation_type == "tenor":
        factor = corr_tmp["theta"] / 100.0
        try:
            floor = corr_tmp["floor"] / 100.0
        except KeyError:
            floor = -1.0
        correlation = _vega_tenor_correlation_calc(numpy.array(values), factor, floor)
    else:
        raise ValueError(f"Invalid correlation type {correlation_type}")

    # provide a 1.0 multiplier for any missing values; otherwise build array.
    rw_multiplier = numpy.ones(len(values))
    if rw_tmp:
        for k, v in rw_tmp.items():
            rw_multiplier[mapping[k]] = v

    return mapping, rw_multiplier, correlation


def _calculate_value_grouping(keys_arr: numpy.ndarray, details: FieldDetails):
    """
    Values are pretty simple since they only support a floating point correlation and multiplier
    however, the correlation should only aply if the numbers are different.  If the numbers are the
    same we should use 1.0.  More numpy magic to compare array to itself.
    """
    mask = (keys_arr[:, None] == keys_arr)

    corr = numpy.ones(mask.shape)
    corr[~mask] = details.correlation

    return details.rw_multiplier, corr


def _calculate_bins_grouping(keys_arr, details):
    # need to handle the nan (which occur due to inflation and basis swaps) and mast those out for the
    # calculation.  We then replace the keys value with the first index in the buckets so that we can
    # generate a valid correlation for it before masking it off.
    mask_vect = (keys_arr == -1)
    keys_arr[keys_arr == -1] = 0
    mask = mask_vect[:, None] * mask_vect

    # this is pretty magic! It is a numpy trick to get the correlation matrix from the indexes in the
    # field values.  It does a 2d lookup on the base correlation array for every element in the keys
    # array to produce a copmlete correlation matrix we can use.
    corr_base = details.correlation
    corr = corr_base[keys_arr][:, keys_arr.T]
    corr[mask] = 1.0

    # more numpy magic - this pulls out the RW for each of the keys that we have so that we can then
    # multiply up those values by the bucket specfic RW.
    rw_multiplier_vect = 1.0
    if details.rw_multiplier is not None:
        rw_multiplier_vect = details.rw_multiplier[keys_arr]
        rw_multiplier_vect[mask_vect] = 1.0

    return corr, rw_multiplier_vect
