from . import constants


def add(instrument):
    instrument.add_parameter("chopper_wavelength_center", value=2.5, comment="Center of wavelength band [AA]")
    instrument.add_declare_var("double", "chopper_position", value=constants.source_to_psc)
    instrument.add_declare_var("double", "speed")
    delay_var = instrument.add_declare_var("double", "delay")

    # Calculate appropriate chopper delay in McStas initialize using C code
    instrument.append_initialize("""
    speed = 2.0*PI/chopper_wavelength_center*K2V;
    delay = chopper_position/speed;
    delay += 0.5*2.86E-3;
    """)

    # Parameter setting chopper speed
    instrument.add_parameter("double", "frequency_multiplier", value=1,
                             comment="[1] Chopper frequency as multiple of source frequency")

    chopper = instrument.add_component("chopper", "DiskChopper",
                                       after="PSC_position", # Place after PSC_position arm in component sequence
                                       RELATIVE="PSC_position") # Place at PSC_position in space
    chopper.theta_0 = 7.0
    chopper.radius = 0.35
    chopper.yheight = 0.05
    chopper.nu = "frequency_multiplier*14.0" # Calculation performed in McStas instrument file
    chopper.delay = delay_var # Declare variable object
