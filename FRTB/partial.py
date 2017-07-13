def merge_partial(a, b):
    """
    :return: Merged value containing the partial combined calculation
    """
    if hasattr(a, '__add__'):
        return a + b

    for key, val in b.items():
        if key not in a:
            a[key] = val
        else:
            a[key] = merge_partial(a[key], val)
    return a
