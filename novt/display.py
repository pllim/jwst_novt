import bqplot
import pandas as pd
import regions

from novt import footprints as fp


# TODO - move to constants/defaults config?
INSTRUMENT_NAMES = {
    'nirspec': 'NIRSpec',
    'nircam long': 'NIRCam Long',
    'nircam short': 'NIRCam Short',
    'nircam_long': 'NIRCam Long',
    'nircam_short': 'NIRCam Short',
}

FOOTPRINT_CONFIG = {
    'NIRSpec': {'func': fp.nirspec_footprint,
                'color': 'red'},
    'NIRCam Long': {'func': fp.nircam_long_footprint,
                    'color': 'blue'},
    'NIRCam Short': {'func': fp.nircam_short_footprint,
                     'color': 'green'}
}


def bqplot_footprint(figure, instrument, ra, dec, pa, wcs,
                     color=None, visible=True, fill='none',
                     alpha=1.0):
    instrument = INSTRUMENT_NAMES[instrument.strip().lower()]

    # get footprint configuration by instrument
    footprint = FOOTPRINT_CONFIG[instrument]['func']
    if color is None:
        color = FOOTPRINT_CONFIG[instrument]['color']

    # make footprint regions
    regs = footprint(ra, dec, pa)

    # get scales from figure
    scales = {'x': figure.interaction.x_scale, 'y': figure.interaction.y_scale}

    marks = []
    for reg in regs:
        pixel_region = reg.to_pixel(wcs)
        if isinstance(pixel_region, regions.PointPixelRegion):
            # instrument center point
            mark = bqplot.Scatter(x=[pixel_region.center.x],
                                  y=[pixel_region.center.y],
                                  scales=scales, colors=[color],
                                  marker='plus')
        else:
            # instrument aperture regions
            x_coords = pixel_region.vertices.x
            y_coords = pixel_region.vertices.y
            mark = bqplot.Lines(x=x_coords, y=y_coords, scales=scales,
                                fill=fill, colors=[color], stroke_width=2,
                                close_path=True, opacities=[alpha],
                                fill_opacities=[alpha])

        mark.visible = visible
        marks.append(mark)

    figure.marks = figure.marks + marks
    return marks


def bqplot_catalog(figure, catalog_file, wcs,
                   colors=None, visible=True, fill=False, alpha=1.0):
    if colors is None:
        colors = ['red', 'yellow']

    # load the source catalog
    catalog = pd.read_table(catalog_file, names=['ra', 'dec', 'flag'],
                            delim_whitespace=True, usecols=[0, 1, 2])

    # sort by flag
    filler = (catalog['flag'] == 'F')
    primary = ~filler

    fill_x, fill_y = wcs.wcs_world2pix(
        catalog['ra'][filler], catalog['dec'][filler], 0)

    primary_x, primary_y = wcs.wcs_world2pix(
        catalog['ra'][primary], catalog['dec'][primary], 0)

    # get scales from figure
    scales = {'x': figure.interaction.x_scale, 'y': figure.interaction.y_scale}

    # scatter plot for primary markers
    primary_markers = bqplot.Scatter(
        x=primary_x, y=primary_y, scales=scales, colors=[colors[0]],
        marker='circle', fill=fill)
    primary_markers.visible = visible
    primary_markers.default_opacities = [alpha]

    # scatter plot for filler markers
    filler_markers = bqplot.Scatter(
        x=fill_x, y=fill_y, scales=scales, colors=[colors[1]],
        marker='circle', fill=fill)
    filler_markers.visible = visible
    filler_markers.default_opacities = [alpha]

    figure.marks = figure.marks + [primary_markers, filler_markers]

    return primary_markers, filler_markers


def remove_bqplot_patches(figure, patches):
    marks = figure.marks.copy()
    for patch in patches:
        marks.remove(patch)
    figure.marks = marks
