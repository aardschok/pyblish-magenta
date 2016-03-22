import pyblish.api


class CollectMayaHistory(pyblish.api.InstancePlugin):
    """Collect history for instances from the Maya scene

    This is separate from Collect Instances so we can target it towards only
    specific family types.

    """

    order = pyblish.api.CollectorOrder + 0.1
    hosts = ["maya"]
    label = "Maya History"
    families = ["rig"]
    verbose = False

    def process(self, instance):
        from maya import cmds

        # Collect the history with long names
        history = cmds.listHistory(instance,
                                   leaf=False) or []
        history = cmds.ls(history, long=True)

        # Combine members with history
        members = instance[:] + history
        members = list(set(members))    # ensure unique

        # Update the instance
        instance[:] = members
