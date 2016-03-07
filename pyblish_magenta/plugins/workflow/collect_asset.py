import pyblish.api
import cquery
import os


class CollectAsset(pyblish.api.ContextPlugin):
    """Collect current asset from the current file"""   

    order = pyblish.api.CollectorOrder + 0.1
    hosts = ["maya"]
    label = "Current Asset"

    def process(self, context):
        
        currentFile = context.data["currentFile"]
        path = os.path.dirname(currentFile)
        asset = cquery.first_match(path, '.Asset', direction=cquery.UP)
        
        if not asset:
            self.log.warning("Couldn't parse current asset")
            return

        self.log.info("Found current asset: {0}".format(asset))
        context.data["asset"] = asset

