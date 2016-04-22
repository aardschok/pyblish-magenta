import pyblish.api


class CollectMetadata(pyblish.api.ContextPlugin):
    """Collect metadata about current asset

    Skips data that is not found in the context with the mapping as used
    in the `mappings` dict. Other collectors can retrieve this data for the
    context to keep this somewhat generic for pipelines.

    """
    order = pyblish.api.CollectorOrder + 0.2
    label = "Metadata"
    families = ["model", "rig", "pointcache", "package"]

    mapping = {

        # origin
        "topic": "topic",
        "author": "user",
        "date": "date",
        "filename": "currentFile",

        # frame ranges
        # At this point when collected the handles are NOT included
        "startFrame": "startFrame",
        "endFrame": "endFrame",
        "handles": "handles",
    }

    def process(self, context):

        metadata = {}
        for key, source in self.mapping.iteritems():
            if source in context.data:
                metadata[key] = context.data.get(source)

        for instance in context:
            instance.set_data("metadata", metadata)

        self.log.info("Collected {0}".format(metadata))
