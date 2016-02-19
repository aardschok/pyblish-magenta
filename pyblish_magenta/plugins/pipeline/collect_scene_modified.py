import pyblish.api


@pyblish.api.log
class CollectSceneSaved(pyblish.api.ContextPlugin):
    """Store scene modified in context"""
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]

    def process(self, context):
        from maya import cmds
        current_file_modified = cmds.file(q=1, modified=True)
        context.set_data('currentFileModified', current_file_modified)
