import pyblish.api
import copy


class CollectMetadata(pyblish.api.ContextPlugin):
    """Collect metadata about current asset

    Skips data that is not found in the context with the mapping as used
    in the `mappings` dict. Other collectors can retrieve this data for the
    context to keep this somewhat generic for pipelines.

    """
    order = pyblish.api.CollectorOrder + 0.2
    label = "Metadata"

    mapping = {
        "topic": "topic",
        "author": "user",
        "date": "date",
        "filename": "currentFile"
    }

    def process(self, context):

        metadata = {}
        for key, source in self.mapping.iteritems():
            if source in context.data:
                metadata[key] = context.data.get(source)

        for instance in context:
            instance_metadata = copy.deepcopy(metadata)
            instance.set_data("metadata", instance_metadata)

        self.log.info("Collected {0}".format(metadata))
