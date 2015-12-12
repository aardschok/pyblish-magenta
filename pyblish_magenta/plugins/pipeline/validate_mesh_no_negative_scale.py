import pyblish.api
from maya import cmds


class ValidateMeshNoNegativeScale(pyblish.api.Validator):
    """Ensure that meshes don't have a negative scale.

    Using the negatively scaled proxies in a VRayMesh results in inverted
    normals. As such we want to avoid this.

    """

    families = ['proxy']
    hosts = ['maya']
    label = 'Mesh No Negative Scale'

    def process(self, instance):
        """Process all the nodes in the instance 'objectSet'"""
        meshes = cmds.ls(instance,
                         type='mesh',
                         long=True,
                         noIntermediate=True)

        invalid = []
        for mesh in meshes:
            transform = cmds.listRelatives(mesh, parent=True, fullPath=True)
            scale = cmds.getAttr("{0}.scale".format(transform))

            if any(x < 0 for x in scale):
                invalid.append(mesh)

        if invalid:
            raise ValueError("Meshes found with negative "
                             "scale: {0}".format(invalid))