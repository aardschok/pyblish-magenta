import pyblish.api
import pyblish_magenta.api
from maya import cmds


class ValidateMeshNonManifold(pyblish.api.InstancePlugin):
    """Ensure that meshes don't have non-manifold edges or vertices"""

    order = pyblish_magenta.api.ValidateMeshOrder
    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)
    label = 'Mesh Non-Manifold Vertices/Edges'

    def process(self, instance):
        """Process all the nodes in the instance 'objectSet'"""
        meshes = cmds.ls(instance, type='mesh', long=True)

        invalid = []
        for mesh in meshes:
            if cmds.polyInfo(mesh, nonManifoldVertices=True) or cmds.polyInfo(mesh, nonManifoldEdges=True):
                invalid.append(mesh)

        if invalid:
            raise ValueError("Meshes found with non-manifold "
                             "edges/vertices: {0}".format(invalid))