import pyblish.api
import pyblish_magenta.api
from maya import cmds


class ValidateDisplayLayerEmpty(pyblish.api.ContextPlugin):
    """Validate there are no empty displayLayers in the scene.

    .. note::
        This is a scene wide validation.

    .. note::
        This filters out checking the display layers
        that exist by default in Maya and are mostly
        hidden to the end user.

    """

    order = pyblish_magenta.api.ValidateContentsOrder
    hosts = ['maya']
    category = 'scene'
    version = (0, 1, 0)
    optional = True
    label = "No Empty Display Layers"

    __skip_layers = ['defaultLayer']

    def _get_empty_layers(self):

        layers = cmds.ls(type='displayLayer')
        empty = []

        for layer in layers:
            if layer in self.__skip_layers:
                continue

            # Skip those that are referenced
            # TODO: Do we really want to skip those that are referened?
            if cmds.referenceQuery(layer, isNodeReferenced=True):
                continue

            members = cmds.editDisplayLayerMembers(layer, q=1)
            if not members:
                empty.append(layer)

        return empty

    def process(self, context):
        """Process the Context"""
        invalid = self._get_empty_layers()

        if invalid:
            raise ValueError("Empty displayLayers found: {0}".format(invalid))

    def repair(self, context):
        """Repair by deleting the empty layers"""
        invalid = self._get_empty_layers()
        cmds.delete(invalid)
