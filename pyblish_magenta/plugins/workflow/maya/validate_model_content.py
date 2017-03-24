import pyblish.api
import pyblish_magenta.api

from pyblish_magenta.action import SelectInvalidAction


class ValidateModelContent(pyblish.api.InstancePlugin):
    """Adheres to the content of 'model' family

    - Must have one top group.
    - Must only contain: transforms, meshes and groups

    """

    order = pyblish_magenta.api.ValidateContentsOrder
    families = ["model"]
    hosts = ["maya"]
    label = "Model Content"
    actions = [SelectInvalidAction]

    @classmethod
    def get_invalid(cls, instance):
        from maya import cmds

        # Ensure only valid node types
        allowed = ('mesh', 'transform', 'nurbsCurve')
        nodes = cmds.ls(instance, long=True)
        valid = cmds.ls(instance, long=True, type=allowed)
        invalid = set(nodes) - set(valid)

        if invalid:
            cls.log.error("These nodes are not allowed: %s" % invalid)
            return list(invalid)

        # Top group
        assemblies = cmds.ls(instance, assemblies=True, long=True)
        print assemblies

        if len(assemblies) != 1:
            cls.log.error("Must have exactly one top group")
            if len(assemblies) == 0:
                cls.log.warning("No top group found. (Are there objects in the instance?)")
            return assemblies or True

        if not valid:
            cls.log.error("No valid nodes in the instance")
            return True

        return []

    def process(self, instance):

        invalid = self.get_invalid(instance)

        if invalid:
            raise RuntimeError("Model content is invalid. See log.")

