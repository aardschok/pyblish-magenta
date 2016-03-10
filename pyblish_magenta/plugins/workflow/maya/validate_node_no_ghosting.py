import pyblish.api
import pyblish_magenta.api
from maya import cmds


class ValidateNodeNoGhosting(pyblish.api.InstancePlugin):
    """Ensure nodes do not have ghosting enabled.

    If one would publish towards a non-Maya format it's likely that stats
    like ghosting won't be exported, eg. exporting to Alembic.

    Instead of creating many micro-managing checks (like this one) to ensure
    attributes have not been changed from their default it could be more
    efficient to export to a format that will never hold such data anyway.

    """

    order = pyblish_magenta.api.ValidateContentsOrder
    families = ['model', 'rig']
    hosts = ['maya']
    optional = False
    version = (0, 1, 0)

    _attributes = {'ghosting': 0}
    label = "No Ghosting"

    def process(self, instance):
        # Transforms and shapes seem to have ghosting
        nodes = cmds.ls(instance, long=True, type=['transform', 'shape'])
        invalid = []
        for node in nodes:
            for attr, required_value in self._attributes.iteritems():
                if cmds.attributeQuery(attr, node=node, exists=True):

                    value = cmds.getAttr('{0}.{1}'.format(node, attr))
                    if value != required_value:
                        invalid.append(node)

        if invalid:
            raise ValueError("Nodes with ghosting enabled found: "
                             "{0}".format(invalid))
