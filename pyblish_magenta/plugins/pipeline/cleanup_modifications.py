import pyblish.api


class CleanupModifications(pyblish.api.Plugin):
    """Save scene when done"""
    label = "Save Scene"
    order = 99.1
    hosts = ["maya"]
    optional = True

    def process(self, context):
        from maya import cmds

        # If the scene wasn't saved we'll raise an error. This is more
        # convenient because otherwise the save command will raise a Maya
        # pop-up plus we can give a clearer error description.
        scene_name = cmds.file(q=1, sn=True)
        if not scene_name:
            raise RuntimeError("Can't save modifications for an unsaved scene")

        cmds.file(save=True)
