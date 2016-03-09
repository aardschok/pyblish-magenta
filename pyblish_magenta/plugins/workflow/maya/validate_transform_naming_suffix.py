import pyblish.api
from maya import cmds


SUFFIX_NAMING_TABLE = {'mesh': ["_GEO", "_GES", "_GEP"],
                       'nurbsCurve': ["_CRV"],
                       'nurbsSurface': ["_NRB"],
                       None: ['_GRP']}

ALLOW_IF_NOT_IN_SUFFIX_TABLE = True


class ValidateTransformNamingSuffix(pyblish.api.InstancePlugin):
    """Validates transform suffix based on the type of its children shapes.

    .. warning::
        This grabs the first child shape as a reference and doesn't use the
        others in the check.

    """

    order = pyblish.api.ValidatorOrder
    families = ['model']
    hosts = ['maya']
    category = 'cleanup'
    optional = True
    version = (0, 1, 0)
    label = 'Suffix Naming Conventions'

    def is_valid_name(self, node_name, shape_type):
        """Return whether node's name is correct.

        The correctness for a transform's suffix is dependent on what
        `shape_type` it holds. E.g. a transform with a mesh might need and
        `_GEO` suffix.

        When `shape_type` is None the transform doesn't have any direct
        children shapes.

        """
        if shape_type not in SUFFIX_NAMING_TABLE:
            return ALLOW_IF_NOT_IN_SUFFIX_TABLE
        else:
            suffices = SUFFIX_NAMING_TABLE[shape_type]
            for suffix in suffices:
                if node_name.endswith(suffix):
                    return True
            return False

    def process(self, instance):
        """Process all the nodes in the instance"""
        transforms = cmds.ls(instance, type='transform', long=True)

        invalid = []
        for transform in transforms:
            shapes = cmds.listRelatives(transform, shapes=True, fullPath=True)

            if not shapes:  # null/group transform
                if not self.is_valid_name(transform, None):
                    invalid.append(transform)

            else:  # based on actual shape type of first child shape
                shape_type = cmds.nodeType(shapes[0])
                if not self.is_valid_name(transform, shape_type):
                    invalid.append(transform)

        if invalid:
            raise ValueError("Incorrectly named geometry "
                             "transforms: {0}".format(invalid))
