import pyblish.api


class CollectMetadataMaya(pyblish.api.ContextPlugin):
    """Collect metadata about referenced files in the scene"""
    order = pyblish.api.CollectorOrder + 0.21
    label = "Maya Metadata"
    hosts = ["maya"]
    families = ["colorbleed.model"
              , "colorbleed.rig"
              , "colorbleed.pointcache"
              , "colorbleed.layout"
              , "colorbleed.look"
              , "colorbleed.package"]

    def process(self, context):
        from maya import cmds

        self.log.info("Collecting references..")

        # Get only valid top level reference nodes
        # This makes it easier than using `cmds.ls` since it lists only
        # top level references, and skips sharedReferenceNode.
        ref_files = cmds.file(query=True, reference=True)
        ref_nodes = [cmds.file(x, query=True, referenceNode=True) for x in ref_files]

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

            object_set = instance.data['objSetName']

            if not cmds.objExists(object_set):
                self.log.info("{0} is not a Maya node".format(object_set))
                continue

            userattrs = dict()
            for attr in cmds.listAttr(object_set, userDefined=True):
                try:
                    value = cmds.getAttr("%s.%s" % (object_set, attr))
                except RuntimeError:
                    continue

                userattrs[attr] = value

            metadata = instance.data("metadata")
            assert metadata
            metadata["references"] = references.values()
            metadata["userattrs"] = userattrs
