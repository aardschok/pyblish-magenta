import pyblish.api
import pyblish_magenta.api
from pyblish_magenta.action import (
    SelectInvalidAction,
    RepairAction
)
from maya import cmds


class ValidateShapeRenderStats(pyblish.api.Validator):
    """Ensure all render stats are set to the default values."""

    order = pyblish_magenta.api.ValidateMeshOrder
    families = ['model']
    hosts = ['maya']
    category = 'model'
    optional = False
    version = (0, 1, 0)
    label = 'Shape Default Render Stats'
    actions = [SelectInvalidAction, RepairAction]

    defaults = {'castsShadows': 1,
                'receiveShadows': 1,
                'motionBlur': 1,
                'primaryVisibility': 1,
                'smoothShading': 1,
                'visibleInReflections': 1,
                'visibleInRefractions': 1,
                'doubleSided': 1,
                'opposite': 0}

    @staticmethod
    def get_invalid(instance):
        # It seems the "surfaceShape" and those derived from it have
        # `renderStat` attributes.
        shapes = cmds.ls(instance, long=True, type='surfaceShape')
        invalid = []
        for shape in shapes:
            for attr, requiredValue in \
                    ValidateShapeRenderStats.defaults.iteritems():

                if cmds.attributeQuery(attr, node=shape, exists=True):
                    value = cmds.getAttr('{node}.{attr}'.format(node=shape,
                                                                attr=attr))
                    if value != requiredValue:
                        invalid.append(shape)

        return invalid

    def process(self, instance):

        invalid = self.get_invalid(instance)

        if invalid:
            raise ValueError("Shapes with non-standard renderStats "
                             "found: {0}".format(invalid))

    @staticmethod
    def repair(instance):

        for shape in ValidateShapeRenderStats.get_invalid(instance):
            for attr, default_value in ValidateShapeRenderStats.defaults.iteritems():

                if cmds.attributeQuery(attr, node=shape, exists=True):
                    plug = '{0}.{1}'.format(shape, attr)
                    value = cmds.getAttr(plug)
                    if value != default_value:
                        cmds.setAttr(plug, default_value)
