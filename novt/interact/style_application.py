import ipywidgets as ipw

from novt.interact.utilities import read_image

__all__ = ['StyleApplication']


class StyleApplication(object):
    """
    Widgets to lay out and style the default application.
    """
    def __init__(self, image_viewer, uploaded_data, nirspec_controls,
                 nircam_controls, overlay_controls, context='notebook'):

        # internal data
        self.title = 'Style Application'
        self.context = context

        self.row_layout = ipw.Layout(
            display='flex', flex_flow='row', align_items='center',
            justify_content='space-between')
        self.column_layout = ipw.Layout(
            display='flex', flex_flow='column', align_items='stretch')

        self.jwst_logo = read_image('JWSTlogo.png')
        self.stsci_logo = read_image('STScIlogo.png')

        self.header = ipw.Box(
            children=[ipw.HTML('<h1>NIRSpec MOS Pre-Imaging Planner</h1>'),
                      ipw.HBox(children=[nirspec_controls.logo,
                                         nircam_controls.logo,
                                         self.jwst_logo, self.stsci_logo])],
            layout=self.row_layout)
        self.footer = ipw.Box(children=[], layout=self.row_layout)

        children = [self.header, uploaded_data.widgets,
                    nirspec_controls.widgets, nircam_controls.widgets]
        if 'notebook' in self.context:
            # in a notebook, display the viewer inline at 100% of cell
            width = '100%'
            children.extend([overlay_controls.widgets, image_viewer.widgets])
        else:
            # in a web app, collapse the viewer and controls and set
            # width to 95% of viewer width
            width = '95vw'
            viewer_with_controls = ipw.Box(
                children=[overlay_controls.widgets, image_viewer.widgets],
                layout=self.column_layout)
            viewer_tab = ipw.Accordion(
                children=[viewer_with_controls],
                layout=self.column_layout, titles=[image_viewer.title])
            children.append(viewer_tab)
        children.append(self.footer)

        # set layout
        self.top_layout = ipw.Layout(
            display='flex', flex_flow='column', align_items='stretch',
            width=width, padding='0px', margin='0px')

        self.widgets = ipw.Box(children=children, layout=self.top_layout)
