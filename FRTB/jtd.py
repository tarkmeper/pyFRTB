import numpy
import copy

from FRTB.engine import Engine, schema_load
from FRTB.product_set import ProductSet, extract_product

_SCHEMA = schema_load("jtd.yaml")

LONG = 0
SHORT = 1


class JTD(Engine):
    """
    This object is structured to store all the JTD values in the following way:
        buckets [ (RISK TYPE, BUCKET INDEX) ] = { NAME: { RATING: RATING, VALUES: [ (LONG, SHORT) ] } }

    Where
        RISK_TYPE -> Represents one of the categories (credit, securitization, correlation)
        BUCKET_INDEX -> The sub-bucket index for this risk type. For example for credit it is one of (sovereign,
            local-government, corporate)
        NAME -> The name of the underlying entity
        RATING -> The rating of the underlying entity
        VALUES -> A list of tupple represent the cumulative long and short JTD values for this entity.  These are sorted
            by seniority, to enable quick offsetting of lower rated shorts with higher rated longs.

    These provide the needed components which can then be added and removed for any given trade allowing for partial
    calculations.
    """

    def __init__(self, details):
        super().__init__("jtd", _SCHEMA, details)

        # Create a mapping for the rating to an array and store their values.
        # a 2-d is used to make it easier to multiply into the final results which we obtain later.
        rating_idx = {}
        rating_array = numpy.zeros((len(details["RW"]), 1))
        for idx, (element, val) in enumerate(details["RW"].items()):
            rating_idx[element] = idx
            rating_array[idx] = float(val) / 100.0

        seniority_lgd = {entry: float(val) / 100.0 for entry, val in details["LGD"].items()}

        industry_mapping = {}
        for category in ['credit']:
            industry_mapping[category] = {}
            for entry, type_list in details[category].items():
                for entry_type in type_list:
                    industry_mapping[category][entry_type] = entry

        self.rating_map = rating_idx
        self.RW = rating_array
        self.seniorty = details["seniority"]
        self.seniority_lgd = seniority_lgd
        self.industry_mapping = industry_mapping
        self.override = ProductSet(details["LGD-override"])
        self.max_maturity = details["maturity"]["max"]
        self.min_maturity = details["maturity"]["min"]
        self.equity_maturity = details["maturity"]["equity"]

        self.array_length = len(self.seniorty)

    def add(self, trade, weight):
        """
        Add a trade to the JTD calculation object; updating the appropriate bucket with the details of the JTD value
        of this trade.

        :param trade:  Trade details
        :param weight:  Weight
        """
        if "jtd" not in trade:
            # If this trade doesn't have a jtd section then we can safely return without updates.
            return

        # determine what type of asset class this is.
        asset_class = trade["asset-class"]
        match asset_class:
            case 'equity' | 'credit':
                section = "credit"
            case 'securitization':
                section = "securitization"
            case 'correlation':
                section = "correlation"
            case _:
                return

        product = extract_product(trade)

        for entry in trade["jtd"]:
            name = entry["name"]

            # identify the bucket we will use for this calculation.
            try:
                bucket_idx = self.industry_mapping[section][entry["sector"]]
            except KeyError:
                bucket_idx = self.industry_mapping[section]["*"]

            if (section, bucket_idx) not in self.buckets:
                self.buckets[(section, bucket_idx)] = {}
            bucket = self.buckets[(section, bucket_idx)]

            if name not in bucket:
                bucket[name] = {"rating": entry["rating"], "values": numpy.zeros((self.array_length, 2))}

            if trade["asset-class"] == "equity":
                seniority = "equity"
                seniority_idx = self.array_length - 1
                maturity = self.equity_maturity
            else:
                seniority = entry["seniority"]
                seniority_idx = self.seniorty.index(seniority)
                maturity = min(self.max_maturity, max(self.min_maturity, trade["maturity"]))

            raw_jtd = entry["value"]
            try:
                lgd = self.override[product] / 100.0
            except KeyError:
                lgd = self.seniority_lgd[seniority]
            jtd = raw_jtd * lgd * maturity

            _add_jtd(bucket[name], seniority_idx, jtd * weight)

    def scale(self, weight):
        """
        Scaling is made more complicated due the fact that we may neeed to swap around the long and short values in
        the vector as we expect both to always be positive.
        """
        for bucket in self.buckets.values():
            for name in bucket.values():
                name["values"] = _scale_values(name["values"], weight)

    def merge(self, other, weight):
        """
        Merge is a combination of the values.  If value doesn't exist currently can just copy structure
        from the other object and adjust by the appropriate weight - however this does require flipping the long
        and short positions.
        """
        for key, value in other.buckets.items():
            if key not in self.buckets:
                self.buckets[key] = copy.deepcopy(value)  # deep copy to reduce risk if updated .
                for name, values in self.buckets[key].items():
                    self.buckets[key][name]["values"] = _scale_values(values["values"], weight)
            else:
                bucket = self.buckets[key]
                for name, details in value.items():
                    if name not in bucket:
                        bucket[name] = copy.deepcopy(details)
                        bucket[name]["values"] = _scale_values(details["values"], weight)
                    else:
                        bucket[name]["values"] += details["values"] * weight
                        ## TODO IMPORTANT
                        ## This needs to be corrected I think if any value goes below 0.  The expectations is that all
                        ## values will be positive at all times....

    def calculate(self, _modifier):
        """
        Calculate the JTD values for the current state of the object.  This will return a dictionary of the total along
        with the total in each bucket
        """
        result = {}
        total = 0.0

        for bucket, details in self.buckets.items():
            bucket_total = self._calculate_bucket(details)
            result[bucket] = bucket_total
            total += bucket_total[0]
        result["total"] = total
        return result

    def _calculate_bucket(self, bucket_details):
        jtd = numpy.zeros((len(self.rating_map), 2))

        for name, name_details in bucket_details.items():
            idx = self.rating_map[name_details["rating"]]
            long, short = _reduce(name_details["values"])
            jtd[idx] += (long, short)

        sum_long = numpy.sum(jtd[:, 0])
        sum_short = numpy.sum(jtd[:, 1])

        # special case if this bucket has been zeroed out - then we can't divide and just return 0
        if sum_long == 0 and sum_short == 0:
            return 0.0, 0.0, 0.0, 0

        # reduce shorts by WTS
        wts = sum_long / (sum_long + sum_short)
        numpy.multiply(wts, jtd[:, 1], out=jtd[:, 1])

        # multiply by RW for each category.
        numpy.multiply(jtd, self.RW, out=jtd)

        # add together - across all risk-ratings.
        totals = numpy.sum(jtd, axis=0)
        bucket_total = max(totals[0] - totals[1], 0.0)

        return bucket_total, totals[0], totals[1], wts


def _scale_values(values, weight):
    """
    # for JTD negative weights have a different effect
    # longs become shorts, shorts become longs, which are different according to regulatory
    # treatment.
    """
    if weight >= 0:
        result = values * weight
    else:
        result = values[:, [1, 0]] * -weight
    return result


def _add_jtd(obj, idx, jtd):
    val = obj["values"][idx]
    if jtd < 0:
        val = (val[LONG], val[SHORT] + (-1 * jtd))
    else:
        val = (val[LONG] + jtd, val[SHORT])
    obj["values"][idx] = val


def _reduce(vect):
    """
    Apply the JTD reduction algorithm to the list offsetting any short values by long values of a higher seniority.
    """
    assert numpy.all(vect >= 0)  # we expect all values here to be positive keeping long and short seperate.

    short_value = 0.0
    long_value = 0.0
    for long, short in reversed(vect):
        short_value += short
        reduction = min(short_value, long)
        short_value -= reduction
        long_value += long - reduction
    return long_value, short_value
