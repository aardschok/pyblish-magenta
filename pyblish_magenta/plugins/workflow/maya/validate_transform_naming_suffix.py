import pyblish.api
import pyblish_magenta.api
from maya import cmds
from pyblish_magenta.action import SelectInvalidAction


SUFFIX_NAMING_TABLE = {'mesh': ["_GEO", "_GES", "_GEP"],
                       'nurbsCurve': ["_CRV"],
                       'nurbsSurface': ["_NRB"],
                       None: ['_GRP']}

ALLOW_IF_NOT_IN_SUFFIX_TABLE = True


class ValidateTransformNamingSuffix(pyblish.api.Validator):
    """Validates transform suffix based on the type of its children shapes.

    Suffices must be:
        - mesh: _GEO or _GES or _GEP
        - nurbsCurve: _CRV
        - nurbsSurface: _NRB
        - null/group: _GRP

    .. warning::
        This grabs the first child shape as a reference and doesn't use the
        others in the check.

    """

    order = pyblish_magenta.api.ValidateContentsOrder
    families = ['model']
    hosts = ['maya']
    category = 'cleanup'
    optional = True
    version = (0, 1, 0)
    label = 'Suffix Naming Conventions'
    actions = [SelectInvalidAction]

    @staticmethod
    def is_valid_name(node_name, shape_type):
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

    @classmethod
    def get_invalid(cls, instance):
        transforms = cmds.ls(instance, type='transform', long=True)

        invalid = []
        for transform in transforms:
            shapes = cmds.listRelatives(transform,
                                        shapes=True,
                                        fullPath=True,
                                        noIntermediate=True)

            shape_type = cmds.nodeType(shapes[0]) if shapes else None
            if not cls.is_valid_name(transform, shape_type):
                invalid.append(transform)

        return invalid

    def process(self, instance):
        """Process all the nodes in the instance"""

        invalid = self.get_invalid(instance)

        if invalid:
            raise ValueError("Incorrectly named geometry "
                             "transforms: {0}".format(invalid))
