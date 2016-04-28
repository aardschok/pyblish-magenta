import pyblish.api
from maya import cmds


class CollectComment(pyblish.api.InstancePlugin):
    """Collect comments for the instances in Maya.

    This adds the `comment` family to any of the instances
    when they have some content in the "notes" area

    """
    label = "Maya Comment"

    order = pyblish.api.CollectorOrder + 0.2
    hosts = ["maya"]

    def process(self, instance):

        node = instance.data.get("objSetName", None)
        if not node:
            return

        node_attr = "{0}.notes".format(node)
        if not cmds.objExists(node_attr):
            return

        comment = cmds.getAttr(node_attr)
        if not comment:
            return

        # Add comment family
        families = instance.data.get("families", [])
        if "comment" not in families:
            families.append("comment")
            instance.data['families'] = families

        # And add the data
        instance.data['comment'] = comment

        self.log.info("Collected comment: {0}".format(comment))
