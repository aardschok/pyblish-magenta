from maya import cmds
import pyblish.api
import pyblish_magenta.api

from pyblish_magenta.action import SelectInvalidAction


class ValidateMeshHasUVs(pyblish.api.InstancePlugin):
    """Validate the current mesh has UVs.

    It validates whether the current UV set has non-zero UVs and
    at least more than the vertex count. It's not really bulletproof,
    but a simple quick validation to check if there are likely
    UVs for every face.
    """

    order = pyblish_magenta.api.ValidateMeshOrder
    families = ['model']
    hosts = ['maya']
    category = 'geometry'
    label = 'Mesh Has UVs'
    actions = [SelectInvalidAction]

    @staticmethod
    def get_invalid(instance):
        invalid = []

        for node in cmds.ls(instance, type='mesh'):
            uv = cmds.polyEvaluate(node, uv=True)

            if uv == 0:
                invalid.append(node)
                continue

            # Must have at least amount of UVs as amount of vertices which
            # provides the assumption that at least every vertex is in the UVs
            vertex = cmds.polyEvaluate(node, vertex=True)
            if uv < vertex:
                invalid.append(node)
                continue

        return invalid

    def process(self, instance):

        invalid = self.get_invalid(instance)

        if invalid:
            raise RuntimeError("Meshes found in instance without "
                               "valid UVs: {0}".format(invalid))
