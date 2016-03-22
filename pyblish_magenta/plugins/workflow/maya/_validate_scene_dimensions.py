import pyblish.api
import pyblish_magenta.api
from maya import cmds


class ValidateSceneDimensions(pyblish.api.InstancePlugin):
    """Validates Scene isn't too big in size.

    Ensures objects are not positioned in the far corners of the 3D space
    beyond the "usual" visible realm. (Far is considered as: 100000 units)

    """

    order = pyblish.api.ValidatorOrder
    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    optional = True
    version = (0, 1, 0)
    label = "Scene Dimensions"

    # The far distance threshold
    __far = 1e5

    def process(self, instance):
        """Process all the nodes in the instance"""
        shapes = cmds.ls(instance, shapes=True, long=True)
        if not shapes: return
        transforms = cmds.listRelatives(shapes, parent=True, fullPath=True)

        invalid = []
        for node in transforms:
            bounding_box = cmds.xform(node,
                                      query=True,
                                      worldSpace=True,
                                      boundingBox=True)
            if any(abs(x) > self.__far for x in bounding_box):
                invalid.append(node)

        if invalid:
            raise ValueError("Nodes found far away or of big size "
                             "('{far}'): {0}".format(invalid, far=self.__far))
