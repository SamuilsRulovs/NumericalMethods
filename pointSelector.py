from matplotlib.widgets import _SelectorWidget
from matplotlib.widgets import ToolHandles
from matplotlib.widgets import Line2D
import matplotlib as mpl
from packaging import version
import utilities as uti


class myPointSelector(_SelectorWidget):
    """
    Select a point from an axes.

    Place vertices with each left mouse click. Calls the onselect function with
    the coordinates of the placed vertices with the right mouse click.

    Parameters
    ----------
    ax : `~matplotlib.axes.Axes`
        The parent axes for the widget.
    h :  float
        The discretization size
    onselect : function
        When right mouse click is pressed,
        the `onselect` function is called and passed a list of the vertices as
        ``[xdata, ydata]`` list.
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
    """

    def __init__(self, ax, h, onselect, useblit=False,
                 lineprops=None, markerprops=None, vertex_select_radius=15):
        self.h = h
        state_modifier_keys = dict(clear='not-applicable', move_vertex='not-applicable',
                                   move_all='not-applicable', move='not-applicable',
                                   square='not-applicable',
                                   center='not-applicable')
        _SelectorWidget.__init__(self, ax, onselect, useblit=useblit,
                                 state_modifier_keys=state_modifier_keys)

        self._xs, self._ys = [0], [0]

        if markerprops is None:
            markerprops = dict(mec='r', mfc='r')
        self._points_handles = ToolHandles(self.ax, self._xs, self._ys,
                                           useblit=useblit,
                                           marker_props=markerprops)
        if version.parse(mpl.__version__) < version.parse("3.5.0"):
            self.artists = [self._points_handles.artist]
        else:
            self._handles_artists = self._points_handles.artists
            lineprops = dict(color='r', linestyle='-', linewidth=2, alpha=0.5, animated=self.useblit, visible=False)
            self.line = Line2D([], [], **lineprops)
            self.ax.add_line(self.line)
            self._selection_artist = self.line

    def onmove(self, event):
        """Cursor move event handler and validator"""
        # Method overrides _SelectorWidget.onmove because the point selector
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
        self._xs[-1], self._ys[-1] = event.xdata, event.ydata
        self._points_handles.set_data(self._xs, self._ys)
        self._draw_point()

    def _press(self, event):
        """Button press event handler"""
        ## if right click pressed
        # if int(event.button) == 3:
        #     self.onselect([[x,y] for x,y in zip(self._xs[0:-1],self._ys[0:-1])])
        ## if left click pressed
        if int(event.button) == 1:
            ix, iy = uti.coords2Index(event.xdata, event.ydata, self.h)
            x, y = uti.index2Coords(ix, iy, self.h)
            self._xs.insert(-1, x)
            self._ys.insert(-1, y)
            self._draw_point()
            self.onselect([[x, y] for x, y in zip(self._xs[0:-1], self._ys[0:-1])])

    def _draw_point(self):
        """Redraw the point based on the new vertex positions."""
        self.set_visible(True)
        self._points_handles.set_data(self._xs, self._ys)
        self.update()
