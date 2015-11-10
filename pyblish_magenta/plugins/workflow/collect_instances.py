import pyblish.api
import pyblish_maya


class CollectInstances(pyblish.api.Collector):
    """Collect instances from the Maya scene

    An instance is identified by having an _INST suffix
    and a .family user-defined attribute.

    All other user-defined attributes of the object set
    is accessible within each instance's data.

    """

    hosts = ["maya"]

    def process(self, context):
        from maya import cmds

        for objset in cmds.ls("*_INST",
                              objectsOnly=True,
                              type='objectSet',
                              long=True,
                              recursive=True):  # Include namespace

            try:
                cmds.getAttr(objset + ".family")
            except ValueError:
                raise Exception("Found: %s found, but no family." % objset)

            instance = context.create_instance(objset)

            for key, default in {
                    "name": cmds.ls(objset, long=False)[0][:-5],
                    "subset": "default"
                    }.iteritems():
                instance.set_data(key, default)

            self.log.info("Found: %s" % objset)

            with pyblish_maya.maintained_selection():

                # Maintain nested object sets
                members = cmds.sets(objset, query=True)
                cmds.select(members, noExpand=True)

                nodes = cmds.file(exportSelected=True,
                                  preview=True,
                                  constructionHistory=True,
                                  force=True)

                nodes = cmds.ls(nodes, long=True)
                self.log.debug("Collecting %s" % nodes)
                instance[:] = nodes

                # Maintain original contents of object set
                instance.set_data("setMembers", members)

            # Get user data from user defined attributes
            user_data = []
            for attr in cmds.listAttr(objset, userDefined=True):
                try:
                    value = cmds.getAttr(objset + "." + attr)
                    user_data.append((attr, value))
                except RuntimeError:
                    continue

            # Assign user data to the instance
            self.log.debug("Collected user data: {0}".format(user_data))
            for key, value in user_data:
                instance.set_data(key, value=value)

            assert instance.has_data("family")

        context[:] = sorted(
            context, key=lambda instance: instance.data("family"))
