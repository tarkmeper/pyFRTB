from FRTB.product_set import ProductSet, extract_product
from FRTB.engine import Engine, schema_load

_SCHEMA = schema_load("residual.yaml")


class Residual(Engine):
    """
    Risiduals are very simple with just specific products configured as either vanilla or exotic and thus having
    certain values assigned to them.  The total exotic and vanilla notional are stored directly.
    """

    def __init__(self, details):
        """
        :param details: Setup the input schema.  This is pre-assumed to have been validated in the Aggregator
        layer against the schema.
        """
        super().__init__("risidual", _SCHEMA, details)

        vanilla_lst = details["vanilla-products"]
        exotics_lst = details["exotic-products"]

        self.vanilla_value = details["vanilla-value"]
        self.exotic_value = details["exotic-value"]
        self.vanilla_products = ProductSet(vanilla_lst)
        self.exotic_products = ProductSet(exotics_lst)

        self.buckets["vanilla"] = 0.0
        self.buckets["exotic"] = 0.0

    def add(self, trade, weight):
        """
        One keynote - weight can be negative to allow for removing a trade.  This is actually fundamentally differnt
        than just "scaling".  This is because unlike scaling two risks in opposite directiosn do not cancel.
        """
        trade_type = extract_product(trade)
        adjusted_notional = float(trade["notional"]) * weight
        if trade_type in self.vanilla_products:
            self.buckets["vanilla"] += adjusted_notional
        elif trade_type in self.exotic_products:
            self.buckets["exotic"] += adjusted_notional

    def scale(self, weight):
        """
         Note that when scaling, positive and negative weights behave the same, i.e. siwtching longs
         to shorts does not change the directionality of the residual risk so never permit scalling by negative
         numbers and instead just scale by the abs weight.
        """
        super().scale(abs(weight))

    def calculate(self, _modifier):
        """ Calculate just prints out the values as this calculation is simple. """
        result = {
            "vanilla": self.buckets["vanilla"],
            "exotic": self.buckets["exotic"],
            "total": self.buckets["vanilla"] * self.vanilla_value + self.buckets["exotic"] * self.exotic_value
        }
        return result
