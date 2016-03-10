import re

import pyblish.api
import pyblish_magenta.api
from maya import cmds


def short_name(node):
    return node.rsplit("|", 1)[-1].rsplit(":", 1)[-1]


class ValidateShapeNoRename(pyblish.api.InstancePlugin):
    """Checks to see if there are nodes with the original names.

    If so it can be a cue for a scene/model that hasn't been cleaned yet.
    This will check for geometry related names, like nurbs & polygons.

    """

    order = pyblish_magenta.api.ValidateContentsOrder
    families = ['model']
    hosts = ['maya']
    category = 'cleanup'
    optional = True
    version = (0, 1, 0)
    label = 'Shape No Default Names'

    # set
    __simpleNames = ['pSphere', 'pCube', 'pCylinder', 'pCone', 'pPlane', 'pTorus',
                     'pPrism', 'pPyramid', 'pPipe', 'pHelix', 'pSolid',
                     'nurbsSphere', 'nurbsCube', 'nurbsCylinder', 'nurbsCone',
                     'nurbsPlane', 'nurbsTorus', 'nurbsCircle', 'nurbsSquare']
    __regex = re.compile('({0})[0-9]?$'.format("|".join(__simpleNames)))

    def process(self, instance):
        """Process all the nodes in the instance 'objectSet'"""
        transforms = cmds.ls(instance, type='transform')

        regex = self.__regex
        
        invalid = []
        for t in transforms:
            if regex.match(short_name(t)):
                invalid.append(t)
            
        if invalid:
            raise ValueError("Non-renamed objects found: {0}".format(invalid))
