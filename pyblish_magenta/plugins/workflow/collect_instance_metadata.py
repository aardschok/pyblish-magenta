
import pyblish.api


class CollectInstanceMetadata(pyblish.api.InstancePlugin):
    """Collect metadata about current asset

    Skips data that is not found in the context with the mapping as used
    in the `mappings` dict. Other collectors can retrieve this data for the
    context to keep this somewhat generic for pipelines.

    """
    order = pyblish.api.CollectorOrder + 0.21
    label = "Instance Metadata"

    mapping = {
        # frame ranges
        # At this point when collected the handles are NOT included
        "startFrame": "startFrame",
        "endFrame": "endFrame",
        "handles": "handles",
    }

    def process(self, instance):

        metadata = instance.data.get("metadata", dict())
        for key, source in self.mapping.iteritems():
            if source in instance.data:
                metadata[key] = instance.data.get(source)

        # Store metadata
        instance.data["metadata"] = metadata

        self.log.info("Collected {0}".format(metadata))
