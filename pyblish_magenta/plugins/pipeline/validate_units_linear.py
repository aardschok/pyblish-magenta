import pyblish.api


@pyblish.api.log
class ValidateUnitsLinear(pyblish.api.ContextPlugin):
    """Scene must be in linear units"""

    order = pyblish.api.ValidatorOrder
    label = "Units (linear)"
    families = ["rig", "model", "pointcache", "curves"]

    def process(self, context):
        units = context.data('linearUnits')

        self.log.info('Units (linear): {0}'.format(units))
        assert units and units == 'cm', (
            "Scene linear units must be centimeters")
