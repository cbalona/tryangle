# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import numpy as np


class TryangleData:
    """
    TryangleData is an internal data structure used by Tryangle which is built
    to work with optimization libraries to allow hyperparameter optimization
    and parallel processing.

    TryangleData can only hold chainladder ``Triangle``'s that are singular in
    the first and second axis. That is, the shape of the ``Triangle`` must be
    (1, 1, n_origin, n_development). The sample_weight must also be singular
    in its development axis, i.e. a shape of (1, 1, n_origin, 1).

    Parameters
    ----------
    triangle : chainladder ``Triangle`` object of shape (1, 1, n_origin, n_development)
        The loss triangle to be reserved.

    sample_weight : chainladder ``Triangle`` object of shape (1, 1, n_origin, 1), default=None
        The exposure data for exposure based methods.
    """

    def __init__(self, triangle, sample_weight=None):
        self.triangle = triangle
        self.sample_weight = sample_weight
        self.shape = self.triangle.shape[2] * self.triangle.shape[3], 1
        self.latest_diagonal = triangle.cum_to_incr().latest_diagonal
        self.actual = self.latest_diagonal[
            self.latest_diagonal.origin < self.latest_diagonal.origin[-1]
        ]

    def __getitem__(self, x):
        indices = np.full((self.shape[0],), False)
        indices[x] = True
        spliced_triangle = self.triangle[indices]
        if self.sample_weight is not None:
            sample_weight_indices = np.array(
                [
                    origin in spliced_triangle.origin
                    for origin in self.sample_weight.origin
                ]
            )
            return TryangleData(
                self.triangle[indices],
                self.sample_weight[sample_weight_indices],
            )
        else:
            return TryangleData(self.triangle[indices], None)
