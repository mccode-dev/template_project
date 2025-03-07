import os

import mcstasscript as ms

from . import guide
from . import choppers
from . import backend
from . import constants # File containing numerical constants necessary in several files


def make(include_choppers=True, include_event_monitors=True, union_detectors=False,
         input_path=None, output_path=None, NeXus=False):

    instrument = ms.McStas_instr("Template", input_path=input_path, output_path=output_path, NeXus=NeXus)

    project_path = os.path.dirname(os.path.abspath(__file__))
    instrument.add_search(os.path.join(project_path, "required_mcstas_components"), help_name="Project path")

    # Source and its parameters
    l_min = instrument.add_parameter("l_min", value=0.5, comment="Minimum simulated wavelength [AA]")
    l_max = instrument.add_parameter("l_max", value=4.0, comment="Maximum simulated wavelength [AA]")
    n_pulses = instrument.add_parameter("int", "n_pulses", value=1, comment="Number of simulated pulses")

    Source = instrument.add_component("Source", "ESS_butterfly")
    Source.set_parameters(sector='"W"', beamline=2,
                          yheight=0.03, cold_frac=0.5,
                          c_performance=1, t_performance=1,
                          Lmin=l_min, Lmax=l_max, n_pulses=n_pulses,
                          acc_power=2)

    # Add the guide system, source component used to set proper focusing
    guide.add(instrument, source=Source)

    # Add the choppers to their positions defined by the add_guide function
    if include_choppers:
        choppers.add(instrument)

    if union_detectors:
        detectors = "union"
    else:
        detectors = "classic"

    backend.add(instrument, detectors=detectors,
                include_event_monitors=include_event_monitors)

    return instrument

