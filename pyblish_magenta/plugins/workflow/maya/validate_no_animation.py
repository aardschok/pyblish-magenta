import pyblish
import pyblish_magenta.api

from pyblish_magenta.action import SelectInvalidAction


class ValidateNoAnimation(pyblish.api.Validator):
    """Ensure no keyframes on nodes in the Instance.

    Even though a Model would extract without animCurves correctly this avoids
    getting different output from a model when extracted from a different
    frame than the first frame. (Might be overly restrictive though)

    """

    order = pyblish_magenta.api.ValidateContentsOrder
    label = "No Animation"
    hosts = ["maya"]
    families = ["colorbleed.model"]
    optional = True
    actions = [SelectInvalidAction]

    @staticmethod
    def get_invalid(instance):
        from maya import cmds

        nodes = instance[:]

        if not nodes:
            return []

        curves = cmds.keyframe(nodes, query=True, name=True)
        if curves:
            return list(set(cmds.listConnections(curves)))

        return []

    def process(self, instance):

        invalid = self.get_invalid(instance)

        if invalid:
            raise RuntimeError("Keyframes found: {0}".format(invalid))
