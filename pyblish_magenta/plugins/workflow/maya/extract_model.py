import os

import pyblish_maya
import pyblish_magenta.api


class ExtractModel(pyblish_magenta.api.Extractor):
    """Extract as Model (Maya Ascii)

    Only extracts contents based on the original "setMembers" data to ensure
    publishing the least amount of required shapes. From that it only takes
    the shapes that are not intermediateObjects

    During export it sets a temporary context to perform a clean extraction.
    The context ensures:
        - Smooth preview is turned off for the geometry
        - Default shader is assigned (no materials are exported)
        - Remove display layers

    """

    label = "Model (Maya ASCII)"
    hosts = ["maya"]
    families = ["colorbleed.model"]
    optional = True

    def process(self, instance):
        from maya import cmds

        # Define extract output file path
        dir_path = self.temp_dir(instance)
        filename = "{0}.ma".format(instance.name)
        path = os.path.join(dir_path, filename)

        # Perform extraction
        self.log.info("Performing extraction..")

        # Get only the shape contents we need in such a way that we avoid
        # taking along intermediateObjects
        members = instance.data("setMembers")
        members = cmds.ls(members,
                          dag=True,
                          shapes=True,
                          type=("mesh", "nurbsCurve"),
                          noIntermediate=True,
                          long=True)

        from cb.utils.maya import context
        with context.no_display_layers(instance):
            with context.displaySmoothness(members,
                                           divisionsU=0,
                                           divisionsV=0,
                                           pointsWire=4,
                                           pointsShaded=1,
                                           polygonObject=1):
                with context.shader(members,
                                    shadingEngine="initialShadingGroup"):
                    with pyblish_maya.maintained_selection():
                        cmds.select(members, noExpand=True)
                        cmds.file(path,
                                  force=True,
                                  typ="mayaAscii",
                                  exportSelected=True,
                                  preserveReferences=False,
                                  channels=False,
                                  constraints=False,
                                  expressions=False,
                                  constructionHistory=False)

        self.log.info("Extracted instance '%s' to: %s" % (instance.name, path))
