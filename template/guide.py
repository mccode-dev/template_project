from . import constants


def add(instrument, source):
    """
    Adds simple guide to instrument

    :param instrument: McStasScript instrument object
    :param source: McStasScript component object for the source used before the guide
    :return: McStasScript instrument object
    """
    source_to_feeder = 2.0

    feeder = instrument.add_component("feeder", "Elliptic_guide_gravity")
    feeder.set_parameters(xwidth=0.08, yheight=0.06, dimensionsAt='"entrance"',
                          l=4.3, m=3, alpha=3.2,
                          linxw=4.5, linyh=2.05,
                          loutxw=0.4, loutyh=0.3)
    feeder.set_AT(source_to_feeder, RELATIVE=source)

    # Update the source focus parameters to match the first guide element
    source.set_parameters(dist=source_to_feeder, focus_xw=feeder.xwidth,
                          focus_yh=1.2*feeder.yheight) # larger focus_yh due to gravity

    # Position of pulse shaping chopper, placed in the choppers.py file
    PSC_position = instrument.add_component("PSC_position", "Arm")
    PSC_position.set_AT(constants.source_to_psc, RELATIVE=source)

    # Define cross section of curved section
    curved_section_width = 0.08
    curved_section_height = 0.12

    # half ellipse
    expanding = instrument.add_component("expanding", "Elliptic_guide_gravity")
    expanding.set_parameters(xwidth=curved_section_width, yheight=curved_section_height, dimensionsAt='"exit"',
                             l=10, m=3, alpha=3.2,
                             linxw=1.2, linyh=0.4)
    expanding.set_parameters(loutxw=expanding.l + expanding.linxw, loutyh=expanding.l + expanding.linyh)
    expanding.set_AT(0.05, RELATIVE=PSC_position)

    # Curved section
    curved_length = 160 - 6.55 - 10 - 10 # full length - chopper
    total_rotation = 1 # total rotation in [deg]
    n_segments = 12
    segment_length = curved_length/n_segments
    segment_rotation = total_rotation/n_segments

    previous_component = expanding
    previous_length = expanding.l
    for index in range(n_segments):
        guide = instrument.add_component("guide_" + str(index), "Guide_gravity")
        guide.set_parameters(w1=curved_section_width, h1=curved_section_height,
                             l=segment_length,
                             m=1.5, alpha=3.0)
        guide.set_AT(previous_length + 3E-3, RELATIVE=previous_component) # Leave 3 mm length between segments
        guide.set_ROTATED([0, segment_rotation, 0], RELATIVE=previous_component)

        # In order to place the next guide element relative to this one, we save it as previous
        previous_component = guide
        previous_length = guide.l

    # half ellipse
    focusing = instrument.add_component("focusing", "Elliptic_guide_gravity")
    focusing.set_parameters(xwidth=curved_section_width, yheight=curved_section_height, dimensionsAt='"entrance"',
                            l=10, m=3, alpha=3.2,
                            loutxw=constants.guide_to_sample + 0.05,
                            loutyh=constants.guide_to_sample + 0.05)
    focusing.set_parameters(linxw=focusing.l + focusing.loutxw, linyh=focusing.l + focusing.loutyh)
    focusing.set_AT(previous_length + 3E-3, RELATIVE=previous_component)

    # guide end is used by backend to place sample position
    guide_end = instrument.add_component("guide_end", "Arm")
    guide_end.set_AT(focusing.l, RELATIVE=focusing)


