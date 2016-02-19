import pyblish.api
from maya import cmds


class ValidateShapeRenderStats(pyblish.api.InstancePlugin):
    """Ensure all render stats are set to the default values."""

    order = pyblish.api.ValidatorOrder
    families = ['model']
    hosts = ['maya']
    category = 'model'
    optional = False
    version = (0, 1, 0)
    label = 'Shape Default Render Stats'

    __renderStats = {'castsShadows': 1,
                     'receiveShadows': 1,
                     'motionBlur': 1,
                     'primaryVisibility': 1,
                     'smoothShading': 1,
                     'visibleInReflections': 1,
                     'visibleInRefractions': 1,
                     'doubleSided': 1,
                     'opposite': 0}

    def process(self, instance):
        # It seems the "surfaceShape" and those derived from it have
        # `renderStat` attributes.
        shapes = cmds.ls(instance, long=True, type='surfaceShape')
        invalid = []
        for shape in shapes:
            for attr, requiredValue in self.__renderStats.iteritems():
                if cmds.attributeQuery(attr, node=shape, exists=True):
                    value = cmds.getAttr('{node}.{attr}'.format(node=shape, attr=attr))
                    if value != requiredValue:
                        invalid.append(shape)

        if invalid:
            raise ValueError("Shapes with non-standard renderStats found: {0}".format(invalid))
