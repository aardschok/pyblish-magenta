import pyblish.api
import pyblish_magenta.api
from pyblish_magenta.action import SelectInvalidAction
from maya import cmds


class ValidateMeshLaminaFaces(pyblish.api.InstancePlugin):
    """Validate meshes don't have lamina faces.
    
    Lamina faces share all of their edges.

    """

    order = pyblish_magenta.api.ValidateMeshOrder
    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)
    label = 'Mesh Lamina Faces'
    actions = [SelectInvalidAction]

    @staticmethod
    def get_invalid(instance):
        meshes = cmds.ls(instance, type='mesh', long=True)
        return [mesh for mesh in meshes if cmds.polyInfo(mesh, laminaFaces=True)]

    def process(self, instance):
        """Process all the nodes in the instance 'objectSet'"""

        invalid = self.get_invalid(instance)

        if invalid:
            raise ValueError("Meshes found with lamina faces: "
                             "{0}".format(invalid))
