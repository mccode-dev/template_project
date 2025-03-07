import numpy as np

from . import constants


def add(instrument, detectors="classic", include_event_monitors=True):

    # inserting basic monitors before sample position to ensure they are placed before any sample inserted later
    guide_end = instrument.get_component("guide_end")

    psd_sample = instrument.add_component("PSD_sample", "PSD_monitor")
    psd_sample.set_AT(constants.guide_to_sample, RELATIVE=guide_end)
    psd_sample.set_parameters(nx=100, ny=100, xwidth=0.03, yheight=0.03,
                              filename='"sample_PSD.dat"', restore_neutron=1)

    wavelength = instrument.add_component("wavelength", "L_monitor")
    wavelength.set_AT(constants.guide_to_sample, RELATIVE=guide_end)
    wavelength.set_parameters(nL=100, Lmin="l_min", Lmax="l_max", # Using parameters defined in make
                              xwidth=0.03, yheight=0.03,
                              filename='"wavelength.dat"', restore_neutron=1)

    # Sample position, an actual sample can be inserted "after" this
    sample_position = instrument.add_component("sample_position", "Arm")
    sample_position.set_AT(constants.guide_to_sample, RELATIVE="guide_end")

    if detectors == "classic":
        add_classic(instrument, include_event_monitors=include_event_monitors)
    elif detectors == "union":
        add_union(instrument, include_event_monitors=include_event_monitors)
    else:
        raise ValueError("Unknown value for detector")


def add_classic(instrument, include_event_monitors=True):
    # Classic detectors

    pixel_min = 0

    theta_bins = 320
    ybins = 20
    monitor = instrument.add_component("Banana_large", "Monitor_nD")
    monitor.set_parameters(radius=3.5, yheight=2.5,
                           filename='"direct_event_banana_signal_large.dat"', restore_neutron=1)
    monitor.options = f'"banana theta bins={theta_bins} limits=[10, 170] y bins={ybins}, neutron pixel min={pixel_min} t, list all neutrons"'
    monitor.set_AT(0.0, RELATIVE="sample_position")

    # increment pixel id using the given detector resolution
    pixel_min += theta_bins*ybins

    theta_bins = 60
    ybins = 20
    monitor = instrument.add_component("Banana_small", "Monitor_nD")
    monitor.set_parameters(radius=3.5, yheight=2.5,
                           filename='"direct_event_banana_signal_small.dat"', restore_neutron=1)
    monitor.options = f'"banana theta bins={theta_bins} limits=[-40, -10] y bins={ybins}, neutron pixel min={pixel_min} t, list all neutrons"'
    monitor.set_AT(0.0, RELATIVE="sample_position")


def add_union(instrument, include_event_monitors=True):
    from mcstasscript.tools.ncrystal_union import add_ncrystal_union_material
    instrument.add_component("init", "Union_init")

    # Air around the sample
    add_ncrystal_union_material(instrument, "Air", "gasmix::air/25C/1.0atm/0.30relhumidity")
    add_ncrystal_union_material(instrument, "He3", "gasmix::He3/25C/5.0atm")

    # Aluminium
    Al_incoherent = instrument.add_component("Al_incoherent", "Incoherent_process")
    Al_incoherent.set_parameters(sigma=4 * 0.0082, unit_cell_volume=66.4)

    Al_powder = instrument.add_component("Al_powder", "Powder_process")
    Al_powder.reflections = '"Al.laz"'

    Al = instrument.add_component("Al", "Union_make_material")
    Al.process_string = '"Al_incoherent,Al_powder"'
    Al.my_absorption = 100 * 4 * 0.231 / 66.4

    tube_angles = np.linspace(10, 170, 16*3)
    #tube_angles.extend(np.linspace(-10, -40, 3*3))

    pixel_min = 0
    for index, angle in enumerate(tube_angles):

        direction = instrument.add_component("direction_" + str(index), "Arm")
        direction.set_RELATIVE("sample_position")
        direction.set_ROTATED([0, angle, 0], RELATIVE="sample_position")

        casing = instrument.add_component("case_" + str(index), "Union_cylinder")
        casing.set_parameters(radius=0.015, yheight=2.5, material_string='"Al"',
                              priority=10 + index)
        casing.set_AT(3.5, RELATIVE=direction)

        """
        gas_name = "gas_" + str(index)
        gas = instrument.add_component(gas_name, "Union_cylinder", RELATIVE=casing)
        gas.set_parameters(radius=casing.radius - 2E-3, yheight=casing.yheight - 0.01,
                           material_string='"He3"', priority=casing.priority + 0.1)

        options = f'"previous, square x bins=3 limits=[-0.03, 0.03] y bins={20}, neutron pixel min={pixel_min} t, list all neutron"'
        abs_logger = instrument.add_component("abs_logger_" + str(index), "Union_abs_logger_nD")
        abs_logger.set_RELATIVE(gas)
        abs_logger.set_parameters(radius=gas.radius, yheight=gas.yheight,
                                  target_geometry=f'"{gas_name}"',
                                  options=options, filename=f'"data_{index}.dat"')
        """

        pixel_min += 3*20

    logger_zx = instrument.add_component("full_logger_space_zx", "Union_logger_2D_space", RELATIVE="sample_position")
    logger_zx.set_parameters(D_direction_1='"z"', D1_min=-4, D1_max=4, n1=400,
                             D_direction_2='"x"', D2_min=-4, D2_max=4, n2=400,
                             filename='"full_logger_zx.dat"')

    logger_xy = instrument.add_component("full_logger_space_xy", "Union_logger_2D_space", RELATIVE="sample_position")
    logger_xy.set_parameters(D_direction_1='"x"', D1_min=-4, D1_max=4, n1=400,
                             D_direction_2='"y"', D2_min=-2, D2_max=2, n2=400,
                             filename='"full_logger_xy.dat"')

    instrument.add_component("master", "Union_master")

    instrument.add_component("stop", "Union_stop")