import unittest

import mcstasscript as ms

import template

import pytest
from itertools import product

# Options for creating the instrument object and combinations to be tested
# These tests compile and run for each combination / test, so limit the number combinations
options = {
    "include_choppers": [True],
    "union_detectors": [False],
    "include_event_monitors": [True],
}

# Generate all combinations
parameter_combinations = list(product(*options.values()))

# Map each combination back to parameter names
named_combinations = [
    dict(zip(options.keys(), values)) for values in parameter_combinations
]


@pytest.mark.parametrize("params", named_combinations)
def test_data_written(params):
    """
    Instrument should compile and write data
    """

    instr = template.make(**params)

    # Set low number of rays
    instr.settings(ncount=1E5)

    # Run instrument simulation
    data = instr.backengine()

    # Check some data returned
    assert data is not None
    assert len(data) > 0



