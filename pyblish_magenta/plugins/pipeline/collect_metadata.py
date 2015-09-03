import os
import pyblish.api


class CollectMetadata(pyblish.api.Collector):
    """Collect metadata about current asset"""
    label = "Metadata"
    families = ["model", "rig", "pointcache", "package"]
    order = pyblish.api.Collector.order + 0.2

    def process(self, context):
        metadata = {
            "project": os.environ["PROJECT"],
            "task": os.environ["TOPICS"].split()[-1],
            "author": context.data("user"),
            "date": context.data("date"),
            "filename": context.data("currentFile").replace(
                "\\", "/").replace(
                os.environ["PROJECTROOT"], "$PROJECTROOT")
        }

        for instance in context:
            instance.set_data("metadata", metadata)

        self.log.info("Collected %s" % instance.data("metadata"))
