import pyblish.api
import pyblish_magenta.api

from pyblish_magenta.action import SelectInvalidAction


class ValidateMeshNonManifold(pyblish.api.InstancePlugin):
    """Ensure that meshes don't have non-manifold edges or vertices"""

    order = pyblish_magenta.api.ValidateMeshOrder
    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)
    label = 'Mesh Non-Manifold Vertices/Edges'
    actions = [SelectInvalidAction]

    @staticmethod
    def get_invalid(instance):
        from maya import cmds

        meshes = cmds.ls(instance, type='mesh', long=True)

        invalid = []
        for mesh in meshes:
            if (cmds.polyInfo(mesh, nonManifoldVertices=True) or
                    cmds.polyInfo(mesh, nonManifoldEdges=True)):
                invalid.append(mesh)

        return invalid

    def process(self, instance):
        """Process all the nodes in the instance 'objectSet'"""

        invalid = self.get_invalid(instance)

        if invalid:
            raise ValueError("Meshes found with non-manifold "
                             "edges/vertices: {0}".format(invalid))
