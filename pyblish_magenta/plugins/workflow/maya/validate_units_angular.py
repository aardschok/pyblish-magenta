import pyblish.api
import pyblish_magenta.api


class ValidateUnitsAngular(pyblish.api.ContextPlugin):
    """Scene angular units must be in degrees"""

    order = pyblish_magenta.api.ValidateSceneOrder
    label = "Units (angular)"
    families = ["rig", "model", "pointcache", "curves"]

    def process(self, context):
        units = context.data('angularUnits')

        self.log.info('Units (angular): {0}'.format(units))
        assert units and units == 'deg', (
            "Scene angular units must be degrees")
