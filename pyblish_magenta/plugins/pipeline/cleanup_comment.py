import pyblish.api


class CleanupComment(pyblish.api.Plugin):
    """Clear working scene of temporal information"""
    label = "Maya Cleanup"
    order = 99
    hosts = ["maya"]
    families = ["comment"]
    optional = True

    def process(self, instance):
        from maya import cmds
        if cmds.objExists(instance.name + ".notes"):
            cmds.setAttr(instance.name + ".notes", "", type="string")
