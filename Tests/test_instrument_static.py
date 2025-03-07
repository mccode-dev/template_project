import unittest

import mcstasscript as ms

import template

import pytest
from itertools import product

# Options for creating the instrument object and combinations to be tested
# These tests compile and run for each combination / test, so limit the number combinations
options = {
    "include_choppers": [False, True],
    "union_detectors": [False, True],
    "include_event_monitors": [False, True],
}

# Generate all combinations
parameter_combinations = list(product(*options.values()))

# Map each combination back to parameter names
named_combinations = [
    dict(zip(options.keys(), values)) for values in parameter_combinations
]


@pytest.mark.parametrize("params", named_combinations)
def test_sample_position(params):
    """
    Instrument must have a component named sample_position of type Arm

    This component is intended to be used for placing sample / sample environment automatically
    """

    instr = template.make(**params)

    assert instr is not None
    assert ms.has_component(instr, component_name="sample_position", component_type="Arm")


@pytest.mark.parametrize("params", named_combinations)
def test_all_parameters_have_default(params):
    """
    All instrument parameters must have default values

    This is considered best practice
    """

    instr = template.make(**params)

    assert instr is not None
    assert ms.all_parameters_set(instr)


@pytest.mark.parametrize("params", named_combinations)
def test_instrument_split_possible(params):
    """
    Test the instrument can be split into two at the start of backend

    To save computation time it is often beneficial to split the instrument into several
    parts using MCPL input and output to bridge these. Then a single simulation of the
    optics / choppers could for example be used for a scan of sample rotations, saving
    computing time. When splitting an instrument into two, its important that the components
    do not have RELATIVE set across the point where the instrument is cut. Instruments
    should have an Arm component at the start of the backend where the instrument can be
    cut, and this test ensures there are no references between the two parts.
    """

    instr = template.make(**params)

    assert instr is not None
    assert instr.subset_check(None, "start_backend") is None # Throws error if check not successful


@pytest.mark.parametrize("params", named_combinations)
def test_RELATIVE_defined(params):
    """
    Check that all positions and rotations are set relative to a valid component name

    The McStas simulation would fail if RELATIVE was used to refer to for example a
    component defined later in the instrument or a misspelled component name.
    """

    instr = template.make(**params)

    assert instr is not None
    assert instr.check_for_relative_errors() is None # Throws error if check not successful
