import bisect
from operator import itemgetter

_SUBSUB_GETTER = itemgetter("asset-class", "base-product", "level2-product", "level3-product")
_SUB_GETTER = itemgetter("asset-class", "base-product", "level2-product")
_GETTER = itemgetter("asset-class", "base-product")


def extract_product(trade):
    """
    Extract the type of product based on the number of levels this product has.

    :param trade: Trade Object (dictionary)
    :return: tuple containing the various levels of the trade.
    """
    if "level3-product" in trade:
        return _SUBSUB_GETTER(trade)
    elif "level2-product" in trade:
        return _SUB_GETTER(trade)
    else:
        return _GETTER(trade)


class ProductSet:
    """
    The product set is a container to identify if a specific product is contained within a hierarchy.

    It stores the hierarchy as a sorted list and makes use of determining where an entry would be inserted
    to determine if this item exists.  An item will either match an element exactly in the sorted list or the bisect
    algorithm will always find the first location to the right of the items parent.  This can help us determine if
    a product is covered by a specific portion of the rules.

    To assist with mapping this support two versions; one where each "key" has a value and is stored as a dictionary
    and the other where the values are stored as a set.
    """
    def __init__(self, objects):
        assert len(objects) > 0
        if isinstance(objects[0], dict):
            srt = sorted(objects, key=itemgetter('key'))
            self.keys = [tuple(f["key"]) for f in srt]
            self.values = [f["value"] for f in srt]
        else:
            self.keys = sorted(map(tuple, objects))

    def _idx(self, item):
        """ Find the index of the object, or if not found the index pointing directly to the right of where
            the object should be.
         """
        idx_left = bisect.bisect_left(self.keys, item)
        if idx_left < len(self.keys) and self.keys[idx_left] == item:
            return idx_left
        # Special case - if not exact match and at left hand side there is no match we need to stop.
        elif idx_left == 0:
            return None
        # if the element to left is a parent of the item we are looking for; we can return that index as object
        # we are looking for
        elif len(self.keys[idx_left - 1]) < len(item) and self.keys[idx_left - 1] == item[
                                                                                     :len(self.keys[idx_left - 1])]:
            return idx_left - 1
        # otherwise this ojbect was not found.
        else:
            return None

    def __contains__(self, item):
        return self._idx(item) is not None

    def __getitem__(self, item):
        idx = self._idx(item)
        if idx is None:
            raise KeyError(f"Item {item} does not exist in product set")
        return self.values[idx]
