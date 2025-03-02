import numpy


def get_cross_correlation(corr_details: dict[dict], mapping: dict) -> numpy.ndarray:
    """
    Given a dictionary of correlation details and a mapping of the fields return a correlation matrix.  This allows data
    to be passed in a Yaml file similar to this

        "yield": { "inflation": 40,  "basis": 0 }
        "inflation": { "basis": 0 }
        "basis": { }

    and turn it into a standard matrix like:

    [   [       1.0     0.4     0 ]
        [       0.4     1.0     0 ]
        [       0.0     0.0     1 ] ]

    :param corr_details:  The input dictionary matrix.
    :param mapping: The mapping of the fields to the index location in the matrix
    :return: resulting correlation matrix.
    """
    corr = numpy.eye(len(mapping))
    for k1, corr_list in corr_details.items():
        i1 = mapping[k1]
        for k2, val in corr_list.items():
            i2 = mapping[k2]
            corr[i2, i1] = val / 100.0
            corr[i1, i2] = val / 100.0
    return corr


def kb_sb_aggregator(kb_vector, sum_vector, correlation, curvature_adjustment=False):
    """
    Perform the "standard" FRTB aggregation which relies on the two mathematical calculations.

         kb_vector -> are the vector defined in section51c of the Basel 352 documentation.
         sum_vector -> are the flast sum of the risk weighted sensitivities

         val1 is the first time under the sqrt in section 51d of the Basel 352 documentation
         val2 is the second term
    """
    assert sum_vector.shape == kb_vector.shape

    assert sum_vector.size > 0

    if sum_vector.size == 1:
        return kb_vector[0]

    val1 = numpy.square(kb_vector).sum()

    tmp = sum_vector.reshape(len(sum_vector), 1)
    matrix = numpy.dot(tmp, tmp.T)
    numpy.fill_diagonal(matrix, 0)

    if curvature_adjustment:
        # Special adjument case described in 53(v) of the basele 352 documentation where a curvature adjustment is
        # applied if both values are negative.
        mask = numpy.logical_and(matrix < 0, matrix.T < 0)
        matrix[mask] = 0.0

    # multiply in the correlation matrix.  This algorithm assumes a constant correlation for all values.
    correlation_adjusted_matrix = numpy.multiply(matrix, correlation)
    val2 = correlation_adjusted_matrix.sum()

    # handle the special case where it is possible due to negative correlations for the value to go below zero.
    if val1 + val2 < 0:
        sum_vector = numpy.maximum(numpy.minimum(sum_vector, kb_vector), -1 * kb_vector)
        return kb_sb_aggregator(kb_vector, sum_vector, correlation)

    return numpy.sqrt(val1 + val2)
