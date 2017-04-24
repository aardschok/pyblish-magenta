import pyblish.api
import pyblish_magenta.api
from maya import cmds

from pyblish_magenta.action import (
    SelectInvalidAction,
    RepairAction
)


class ValidateMeshNormalsUnlocked(pyblish.api.Validator):
    """Validate all meshes in the instance have unlocked normals

    These can be unlocked manually through:
        Modeling > Mesh Display > Unlock Normals

    """

    order = pyblish_magenta.api.ValidateMeshOrder
    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    version = (0, 1, 0)
    label = 'Mesh Normals Unlocked'
    actions = [SelectInvalidAction, RepairAction]
    optional = True

    @staticmethod
    def has_locked_normals(mesh):
        """Return whether a mesh node has locked normals"""

        mesh_vertexface = cmds.polyListComponentConversion(mesh,
                                                           toVertexFace=True)
        locked_normals = cmds.polyNormalPerVertex(mesh_vertexface, q=1,
                                                  freezeNormal=True)
        if any(locked_normals):
            return True
        else:
            return False

    @classmethod
    def get_invalid(cls, instance):
        """Return the meshes with locked normals in instance"""

        meshes = cmds.ls(instance, type='mesh', long=True)
        return [mesh for mesh in meshes if cls.has_locked_normals(mesh)]

    def process(self, instance):
        """Raise invalid when any of the meshes have locked normals"""

        invalid = self.get_invalid(instance)

        if invalid:
            raise ValueError("Meshes found with "
                             "locked normals: {0}".format(invalid))

    @classmethod
    def repair(cls, instance):
        """Unlocks all normals on the meshes in this instance."""
        invalid = cls.get_invalid(instance)
        for mesh in invalid:
            cmds.polyNormalPerVertex(mesh, unFreezeNormal=True)
