import pyblish.api
import pyblish_maya


def get_upstream_hierarchy_fast(nodes):
    """Passed in nodes must be long names!"""

    matched = set()
    parents = []

    for node in nodes:
        hierarchy = node.split("|")
        num = len(hierarchy)
        for x in range(1, num-1):
            parent = "|".join(hierarchy[:num-x])
            if parent in parents:
                break
            else:
                parents.append(parent)
                matched.add(parent)

    return parents


class CollectInstances(pyblish.api.ContextPlugin):
    """Collect instances from the Maya scene

    An instance is identified by having an _INST suffix
    and a .family user-defined attribute.

    All other user-defined attributes of the object set
    is accessible within each instance's data.

    """

    order = pyblish.api.CollectorOrder
    hosts = ["maya"]
    verbose = False

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
                self.log.error("Found: %s found, but no family." % objset)
                continue

            instance = context.create_instance(objset)
            short_name = objset.rsplit("|", 1)[-1].rsplit(":", 1)[-1]
            for key, default in {
                    "name": short_name[:-5],
                    "subset": "default"
                    }.iteritems():
                instance.set_data(key, default)

            self.log.info("Found: %s" % objset)

            with pyblish_maya.maintained_selection():

                # Maintain nested object sets
                members = cmds.sets(objset, query=True)
                members = cmds.ls(members, long=True)

                # Include all parents and children
                parents = cmds.listRelatives(members,
                                             allDescendents=True,
                                             fullPath=True,
                                             noIntermediate=True) or []

                # Include all children
                children = get_upstream_hierarchy_fast(members)

                nodes = members + parents + children

                # Include all history
                include_history = False  # disable for now
                if include_history:
                    history = cmds.listHistory(nodes,
                                               leaf=False) or []
                    nodes += history

                if self.verbose:
                    self.log.debug("Collecting nodes: %s" % nodes)
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

            if self.verbose:
                self.log.debug("Collected user data: {0}".format(user_data))

            # Assign user data to the instance
            for key, value in user_data:
                instance.set_data(key, value=value)

            assert instance.has_data("family"), "No family data in instance"

        context[:] = sorted(
            context, key=lambda instance: instance.data("family"))
