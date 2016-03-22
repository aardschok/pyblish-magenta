import os
import json
import pyblish_magenta.api


class ExtractOrigin(pyblish_magenta.api.Extractor):
    """Extract origin metadata from scene"""

    label = "Metadata"
    families = ["model", "rig", "pointcache", "look", "layout"]

    def process(self, instance):
        temp_dir = self.temp_dir(instance)
        temp_file = os.path.join(temp_dir, "metadata.meta")

        metadata = instance.data("metadata")
        self.log.info("Extracting %s" % metadata)
        with open(temp_file, "w") as f:
            json.dump(metadata, f, indent=2, sort_keys=True)

        self.log.info("Written to %s" % temp_file)
