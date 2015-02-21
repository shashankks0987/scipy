"""
This module provides functions to perform full Procrustes analysis.

This code was originally written by Justin Kucynski and ported over from
scikit-bio by Yoshiki Vazquez-Baeza.
"""

from __future__ import absolute_import, division, print_function

import numpy as np
from scipy.linalg import orthogonal_procrustes


__all__ = ['procrustes']


def procrustes(data1, data2):
    r"""Procrustes analysis, a similarity test for two data sets

    Each input matrix is a set of points or vectors (the rows of the matrix).
    The dimension of the space is the number of columns of each matrix. Given
    two identically sized matrices, procrustes standardizes both such that:

    - :math:`tr(AA^{T}) = 1`.

    - Both sets of points are centered around the origin.

    Procrustes ([1]_, [2]_) then applies the optimal transform to the second
    matrix (including scaling/dilation, rotations, and reflections) to minimize
    :math:`M^{2}=\sum(data1-data2)^{2}`, or the sum of the squares of the
    pointwise differences between the two input datasets.

    This function was not designed to handle datasets with different numbers of
    datapoints (rows).  If two data sets have different dimensionality
    (different number of columns), simply add columns of zeros the smaller of
    the two.

    Parameters
    ----------
    data1 : array_like
        matrix, n rows represent points in k (columns) space data1 is the
        reference data, after it is standardised, the data from data2 will
        be transformed to fit the pattern in data1 (must have >1 unique
        points).

    data2 : array_like
        n rows of data in k space to be fit to data1.  Must be the  same
        shape (numrows, numcols) as data1 (must have >1 unique points).

    Returns
    -------
    mtx1 : array_like
        a standardized version of data1
    mtx2 : array_like
        the orientation of data2 that best fits data1. Centered, but not
        necessarily :math:`tr(AA^{T}) = 1`.
    disparity : float
        :math:`M^{2}` as defined above.

    Raises
    ------
    ValueError
        If the input arrays are not two-dimensional.
        If the shape of the input arrays is different.
        If the input arrays have zero columns or zero rows.

    See Also
    --------
    orthogonal_procrustes

    Notes
    -----
    - The disparity should not depend on the order of the input matrices, but
      the output matrices will, as only the first output matrix is guaranteed
      to be scaled such that :math:`tr(AA^{T}) = 1`.

    - Duplicate data points are generally ok, duplicating a data point will
      increase its effect on the procrustes fit.

    - The disparity scales as the number of points per input matrix.

    References
    ----------
    .. [1] Krzanowski, W. J. (2000). "Principles of Multivariate analysis".
    .. [2] Gower, J. C. (1975). "Generalized procrustes analysis".

    Examples
    --------
    >>> import numpy as np
    >>> from scipy.spatial import procrustes
    # the b matrix is a rotated, shifted, scaled and mirrored version of a
    >>> a = np.array([[1, 3], [1, 2], [1, 1], [2, 1]], 'd')
    >>> b = np.array([[4, -2], [4, -4], [4, -6], [2, -6]], 'd')
    >>> mtx1, mtx2, disparity = procrustes(a, b)
    >>> round(disparity)
    0.0

    """

    data1 = np.asarray(data1, dtype=np.double)
    data2 = np.asarray(data2, dtype=np.double)

    if data1.ndim != 2 or data2.ndim != 2:
        raise ValueError("Input matrices must be two-dimensional")
    num_rows, num_cols = np.shape(data1)
    if (num_rows, num_cols) != np.shape(data2):
        raise ValueError("Input matrices must be of same shape")
    if num_rows == 0 or num_cols == 0:
        raise ValueError("Input matrices must be >0 rows and >0 cols")

    # translate all the data to the origin
    mtx1 = data1-np.mean(data1, 0)
    mtx2 = data2-np.mean(data2, 0)

    if (not np.any(mtx1)) or (not np.any(mtx2)):
        raise ValueError("input matrices must contain >1 unique points")

    # change scaling of data (in rows) such that trace(mtx*mtx') = 1
    mtx1 = mtx1/np.linalg.norm(mtx1)
    mtx2 = mtx2/np.linalg.norm(mtx2)

    # transform mtx2 to minimize disparity
    R, s = orthogonal_procrustes(mtx1, mtx2)
    mtx2 = np.dot(mtx2, R.T) * s

    # measure the dissimilarity between the two datasets
    disparity = np.sum(np.square(mtx1 - mtx2))

    return mtx1, mtx2, disparity

