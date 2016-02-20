import pyblish.api


class CleanupComment(pyblish.api.InstancePlugin):
    """Clear working scene of temporal information"""
    label = "Cleanup Maya Comment"
    order = 99
    hosts = ["maya"]
    families = ["comment"]
    optional = True

    def process(self, instance):
        from maya import cmds
        if cmds.objExists(instance.name + ".notes"):
            cmds.setAttr(instance.name + ".notes", "", type="string")
