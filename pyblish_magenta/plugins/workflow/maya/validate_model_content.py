import pyblish.api
import pyblish_magenta.api


class ValidateModelContent(pyblish.api.InstancePlugin):

    order = pyblish_magenta.api.ValidateContentsOrder
    families = ["model"]
    hosts = ["maya"]
    label = "Model Content"

    def process(self, instance):
        from maya import cmds
        allowed = ('mesh', 'transform', 'nurbsCurve')

        nodes = cmds.ls(instance, long=True)
        valid = cmds.ls(instance, long=True, type=allowed)

        [self.log.info("Considering %s.." % node) for node in nodes]
        invalid = set(nodes) - set(valid)

        assert not invalid, "These nodes are not allowed: %s" % invalid
