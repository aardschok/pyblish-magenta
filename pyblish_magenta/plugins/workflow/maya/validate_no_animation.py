import pyblish
import pyblish_magenta.api


class ValidateNoAnimation(pyblish.api.InstancePlugin):
    """Ensure no keyframes on nodes in the Instance.

    Even though a Model would extract without animCurves correctly this avoids
    getting different output from a model when extracted from a different
    frame than the first frame. (Might be overly restrictive though)

    """

    order = pyblish_magenta.api.ValidateContentsOrder
    label = "No Animation"
    hosts = ["maya"]
    families = ["model"]
    optional = True

    def process(self, instance):
        from maya import cmds

        curves = cmds.keyframe(instance, q=1, name=True)
        if curves:
            invalid = list(set(cmds.listConnections(curves)))
            raise RuntimeError("Keyframes found: {0}".format(invalid))
