import pyblish.api


class CleanupModifications(pyblish.api.Plugin):
    """Save scene when done"""
    label = "Save Scene"
    order = 99.1
    hosts = ["maya"]
    optional = True

    def process(self, context):
        from maya import cmds
        cmds.file(save=True)
