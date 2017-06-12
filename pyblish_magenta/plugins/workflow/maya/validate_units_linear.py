import pyblish.api
import pyblish_magenta.api


class ValidateUnitsLinear(pyblish.api.ContextPlugin):
    """Scene must be in linear units"""

    order = pyblish_magenta.api.ValidateSceneOrder
    label = "Units (linear)"
    families = ["colorbleed.rig",
                "colorbleed.model",
                "colorbleed.pointcache",
                "colorbleed.curves"]

    def process(self, context):
        units = context.data('linearUnits')

        self.log.info('Units (linear): {0}'.format(units))
        assert units and units == 'cm', ("Scene linear units must "
                                         "be centimeters")
