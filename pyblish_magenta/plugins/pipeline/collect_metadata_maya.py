import os
import pyblish.api


class CollectMetadataMaya(pyblish.api.Collector):
    """Collect metadata about referenced files in the scene"""
    label = "Maya Metadata"
    hosts = ["maya"]
    families = ["model", "rig", "pointcache", "package"]
    order = pyblish.api.Collector.order + 0.21

    def process(self, context):
        from maya import cmds

        self.log.info("Collecting references..")

        references = dict()
        for reference in cmds.ls(type="reference"):
            if reference in ("sharedReferenceNode",):
                continue

            # Only consider top-level references
            reference = cmds.referenceQuery(reference,
                                            referenceNode=True,
                                            topReference=True)

            filename = cmds.referenceQuery(
                reference,
                filename=True,
                withoutCopyNumber=True  # Exclude suffix {1}
                ).replace("\\", "/")

            if filename in references:
                continue

            references[filename] = {
                "node": reference,
                "filename": filename
            }

            self.log.info("Collecting %s" % references[filename])

        for instance in context:
            userattrs = dict()
            for attr in cmds.listAttr(instance.id, userDefined=True):
                try:
                    value = cmds.getAttr(instance.id + "." + attr)
                except RuntimeError:
                    continue

                userattrs[attr] = value

            metadata = instance.data("metadata")
            assert metadata
            metadata["references"] = references.values()
            metadata["userattrs"] = userattrs
