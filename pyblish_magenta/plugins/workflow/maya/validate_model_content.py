import pyblish.api
import pyblish_magenta.api


class ValidateModelContent(pyblish.api.InstancePlugin):
    """Adheres to the content of 'model' family

    - Must have one top group named: geo_GRP
    - Must only contain: transforms, meshes and groups

    """

    order = pyblish_magenta.api.ValidateContentsOrder
    families = ["model"]
    hosts = ["maya"]
    label = "Model Content"

    def process(self, instance):
        from maya import cmds

        # Ensure only valid node types
        allowed = ('mesh', 'transform', 'nurbsCurve')
        nodes = cmds.ls(instance, long=True)
        valid = cmds.ls(instance, long=True, type=allowed)
        invalid = set(nodes) - set(valid)

        assert not invalid, "These nodes are not allowed: %s" % invalid

        # Top group
        assemblies = cmds.ls(instance, assemblies=True, long=True)

        if len(assemblies) != 1:
            raise RuntimeError("Model must have one top group")

        if assemblies[0] != "|geo_GRP":
            raise RuntimeError("Top group must be named 'geo_GRP'")

