import pyblish.api

from maya import cmds
from maya import mel


class CollectMayaUnits(pyblish.api.ContextPlugin):
    """Collect Maya's scene units."""

    label = "Maya Units"
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]

    def process(self, context):

        # Get the current linear units
        units = cmds.currentUnit(query=True, linear=True)

        # Get the current angular units ('deg' or 'rad')
        units_angle = cmds.currentUnit(query=True, angle=True)

        # Get the current time units
        # Using the mel command is simpler than using
        # `mc.currentUnit(q=1, time=1)`. Otherwise we
        # have to parse the returned string value to FPS
        fps = mel.eval('currentTimeUnitToFPS()')

        context.set_data('linearUnits', units)
        context.set_data('angularUnits', units_angle)
        context.set_data('fps', fps)
