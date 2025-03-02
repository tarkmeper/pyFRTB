from FRTB.product_set import ProductSet


def test_product_set():
    product_list = [
        ["ELF"],
        ["ABC", "AB", "A"],
        ["BCD", "B"],
    ]

    ps = ProductSet(product_list)

    # Any product that is listed in the product list, or items hierarchically below those products
    # are included.  Otherwise tehy are excluded.
    assert ("ELF",) in ps
    assert ("ELF", "A") in ps
    assert ("BCD",) not in ps
    assert ("BCD", "B") in ps
    assert ("BCD", "B", "A") in ps

    assert ("AAA",) not in ps


def test_mapping_product_set():
    product_list = [
        {"key": ["ELF"], "value": 10},
        {"key": ["ABC", "AB", "A"], "value": 13},
        {"key": ["BCD", "B"], "value": 15},

    ]

    ps = ProductSet(product_list)

    # Any product that is listed in the product list, or items hierarchically below those products
    # are included.  Otherwise tehy are excluded.
    assert ("ELF",) in ps
    assert ps[("ELF",)] == 10
    assert ("ELF", "A") in ps
    assert ps[("ELF", "A")] == 10
    assert ("BCD",) not in ps
    assert ("BCD", "B") in ps
    assert ps[("BCD", "B")] == 15
    assert ("BCD", "B", "A") in ps
    assert ps[("BCD", "B", "A")] == 15