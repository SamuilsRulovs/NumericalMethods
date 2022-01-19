import matplotlib.pyplot as plt

from matplotlib.widgets import _SelectorWidget
from matplotlib.widgets import Line2D
from matplotlib.widgets import ToolHandles
import matplotlib as mpl
from packaging import version

import numpy as np
import utilities as uti


class myPolygonSelector(_SelectorWidget):
    """
    Select a polygon region of an axes.

    Place vertices with each mouse click, and make the selection by completing
    the polygon (clicking on the first vertex). Hold the *ctrl* key and click
    and drag a vertex to reposition it (the *ctrl* key is not necessary if the
    polygon has already been completed). Hold the *shift* key and click and
    drag anywhere in the axes to move all vertices. Press the *esc* key to
    start a new polygon.

    For the selector to remain responsive you must keep a reference to
    it.

    Parameters
    ----------
    ax : `~matplotlib.axes.Axes`
        The parent axes for the widget.
    h :  float
        The discretization size
    onselect : function
        When a polygon is completed or modified after completion,
        the `onselect` function is called and passed a list of the vertices as
        ``(xdata, ydata)`` tuples.
    useblit : bool, optional
    lineprops : dict, optional
        The line for the sides of the polygon is drawn with the properties
        given by `lineprops`. The default is ``dict(color='k', linestyle='-',
        linewidth=2, alpha=0.5)``.
    markerprops : dict, optional
        The markers for the vertices of the polygon are drawn with the
        properties given by `markerprops`. The default is ``dict(marker='o',
        markersize=7, mec='k', mfc='k', alpha=0.5)``.
    vertex_select_radius : float, optional
        A vertex is selected (to complete the polygon or to move a vertex)
        if the mouse click is within `vertex_select_radius` pixels of the
        vertex. The default radius is 15 pixels.

    Examples ( From matplotlib )
    --------
    :doc:`/gallery/widgets/polygon_selector_demo`
    """

    def __init__(self, ax, h, onselect, useblit=False,
                 lineprops=None, markerprops=None, vertex_select_radius=15):
        # The state modifiers 'move', 'square', and 'center' are expected by
        # _SelectorWidget but are not supported by PolygonSelector
        # Note: could not use the existing 'move' state modifier in-place of
        # 'move_all' because _SelectorWidget automatically discards 'move'
        # from the state on button release.
        state_modifier_keys = dict(clear='not-applicable', move_vertex='not-applicable',
                                   move_all='not-applicable', move='not-applicable',
                                   square='not-applicable',
                                   center='not-applicable')
        _SelectorWidget.__init__(self, ax, onselect, useblit=useblit,
                                 state_modifier_keys=state_modifier_keys)

        self._xs, self._ys = [0], [0]
        self._polygon_completed = False

        if lineprops is None:
            lineprops = dict(color='r', linestyle='-', linewidth=2, alpha=0.5, animated=self.useblit)
        self.line = Line2D(self._xs, self._ys, **lineprops)
        self.ax.add_line(self.line)

        if markerprops is None:
            markerprops = dict(mec='r', mfc=lineprops.get('color', 'r'))
        self._polygon_handles = ToolHandles(self.ax, self._xs, self._ys,
                                            useblit=self.useblit,
                                            marker_props=markerprops)

        self.vertex_select_radius = vertex_select_radius

        if version.parse(mpl.__version__) < version.parse("3.5.0"):
            self.artists = [self.line, self._polygon_handles.artist]
        else:
            self._handles_artists = self._polygon_handles.artists
            self._selection_artist = self.line

        self.set_visible(True)
        self.h = h

        # self._selection_artist = [self.line]        # self.
        # try:

    def _release(self, event):
        """Button release event handler"""
        # Complete the polygon.
        if (len(self._xs) > 3
                and self._xs[-1] == self._xs[0]
                and self._ys[-1] == self._ys[0]):
            self._polygon_completed = True

        # Place new vertex.
        elif not self._polygon_completed:
            ix, iy = uti.coords2Index(event.xdata, event.ydata, self.h)
            x, y = uti.index2Coords(ix, iy, self.h)
            self._xs.insert(-1, x)
            self._ys.insert(-1, y)

        if self._polygon_completed:
            self.onselect(self.verts)

    def onmove(self, event):
        """Cursor move event handler and validator"""
        # Method overrides _SelectorWidget.onmove because the polygon selector
        # needs to process the move callback even if there is no button press.
        # _SelectorWidget.onmove include logic to ignore move event if
        # eventpress is None.
        if not self.ignore(event):
            event = self._clean_event(event)
            self._onmove(event)
            return True
        return False

    def _onmove(self, event):
        """Cursor move event handler"""
        # Move the active vertex (ToolHandle).
        if self._polygon_completed:
            return
        # Position pending vertex.
        else:
            # Calculate distance to the start vertex.
            x0, y0 = self.line.get_transform().transform((self._xs[0],
                                                          self._ys[0]))
            ix, iy = uti.coords2Index(event.xdata, event.ydata, self.h)
            xCoordSys, yCoordSys = uti.index2Coords(ix, iy, self.h)
            x1, y1 = self.line.get_transform().transform((xCoordSys, yCoordSys))
            v0_dist = np.hypot(x0 - x1, y0 - y1)
            # Lock on to the start vertex if near it and ready to complete.
            if len(self._xs) > 3 and v0_dist < self.vertex_select_radius:
                self._xs[-1], self._ys[-1] = self._xs[0], self._ys[0]
            else:
                self._xs[-1], self._ys[-1] = event.xdata, event.ydata

        self.set_visible(True)
        self._draw_polygon()

    def _draw_polygon(self):
        self.set_visible(True)
        """Redraw the polygon based on the new vertex positions."""
        self.line.set_data(self._xs, self._ys)
        # Only show one tool handle at the start and end vertex of the polygon
        # if the polygon is completed or the user is locked on to the start
        # vertex.
        if ((len(self._xs) > 3
             and self._xs[-1] == self._xs[0]
             and self._ys[-1] == self._ys[0])):
            self._polygon_handles.set_data(self._xs[:-1], self._ys[:-1])
        else:
            self._polygon_handles.set_data(self._xs, self._ys)
        self.update()

    @property
    def verts(self):
        """The polygon vertices, as a list of ``(x, y)`` pairs."""
        return list(zip(self._xs[:-1], self._ys[:-1]))
