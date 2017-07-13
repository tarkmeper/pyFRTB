"""
Aggregation functions are used to combine the results of various buckets.
"""
import numpy


# noinspection PyTypeChecker
def constant_aggregator(vect, factor):
    """
    Aggregate a numpy vector using a constant correlation value
    :param vect:    Vector of values to aggregate
    :param factor:  The constant correlation factor to use between elements
    :return: The aggregated value
    """
    matrix = vect.reshape(len(vect), 1)
    tmp = numpy.dot(matrix, matrix.T)
    corr = tmp * factor + numpy.diag(tmp.diagonal() * (1 - factor))
    return numpy.sum(corr)


def matrix_aggregator(vector, matrix):
    """
    Perform a numpy based aggregation when the correlations are stored in a matrix
    :param vector: Values to aggregate
    :param matrix:  A matrix of correlation values
    :return: The aggregated value
    """
    assert len(vector) == matrix.shape[0]
    assert len(vector) == matrix.shape[1]
    return numpy.dot(numpy.dot(vector, matrix), vector.T)
