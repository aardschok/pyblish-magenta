import pyblish.api


class CollectSceneSaved(pyblish.api.ContextPlugin):
    """Store scene modified in context"""

    label = "Maya Scene Modified"
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]

    def process(self, context):
        from maya import cmds
        current_file_modified = cmds.file(q=1, modified=True)
        context.set_data('currentFileModified', current_file_modified)
