import os.path

from maya import cmds
import pyblish.api

import pyblish_magenta.schema


@pyblish.api.log
class SelectWorkFile(pyblish.api.Selector):
    """ Inject current work file information into the context """
    order = pyblish.api.Selector.order - 0.1
    hosts = ["maya"]

    def process(self, context):
        self.log.info("Selecting work file..")

        # Get the filename
        scene_name = cmds.file(q=1, sceneName=True)
        if not scene_name:
            # file not saved
            self.log.error("Scene has not been saved.")
            return

        # Parse with schema
        schema = pyblish_magenta.schema.load()
        data = schema.get("model.dev").parse(scene_name)

        # Store the working data
        context.set_data('work_file', scene_name)
        context.set_data('work_root', data['root'])
        context.set_data('work_asset', data['asset'])
        context.set_data('work_container', data['container'])

