import os
import pyblish.api


class CollectMetadataMaya(pyblish.api.ContextPlugin):
    """Collect metadata about referenced files in the scene"""
    order = pyblish.api.CollectorOrder + 0.21
    label = "Maya Metadata"
    hosts = ["maya"]
    families = ["model", "rig", "pointcache", "package"]

    def process(self, context):
        from maya import cmds

        self.log.info("Collecting references..")

        # Get only valid top level reference nodes
        # This makes it easier than using `cmds.ls` since it lists only
        # top level references, and skips sharedReferenceNode.
        ref_files = cmds.file(q=1, reference=1)
        ref_nodes = [cmds.file(x, q=1, referenceNode=True) for x in ref_files]

        references = dict()
        for reference in ref_nodes:

            # Ensure only top-level references
            assert cmds.referenceQuery(reference,
                                       referenceNode=True,
                                       topReference=True) == reference

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

            if not cmds.objExists(instance.id):
                self.log.info("{0} is not a Maya node".format(instance.id))
                continue

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
