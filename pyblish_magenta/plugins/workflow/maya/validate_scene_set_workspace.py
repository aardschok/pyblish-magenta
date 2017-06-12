import pyblish.api
import pyblish_magenta.api
import maya.cmds as cmds
import os


def is_subdir(path, root_dir):
    """ Returns whether path is a subdirectory (or file) within root_dir """
    path = os.path.realpath(path)
    root_dir = os.path.realpath(root_dir)

    # If not on same drive
    if os.path.splitdrive(path)[0] != os.path.splitdrive(root_dir)[0]:
        return False

    # Get 'relative path' (can contain ../ which means going up)
    relative = os.path.relpath(path, root_dir)

    # Check if the path starts by going up, if so it's not a subdirectory. :)
    if relative.startswith(os.pardir) or relative == os.curdir:
        return False
    else:
        return True


class ValidateSceneSetWorkspace(pyblish.api.ContextPlugin):
    """Validate the scene is inside the currently set Maya workspace"""

    order = pyblish_magenta.api.ValidatePipelineOrder
    hosts = ['maya']
    families = ['colorbleed.model']
    category = 'scene'
    version = (0, 1, 0)
    label = 'Maya Workspace Set'

    def process(self, context):

        scene_name = cmds.file(q=1, sceneName=True)
        if not scene_name:
            raise RuntimeError("Scene hasn't been saved. Workspace can't be validated.")

        root_dir = cmds.workspace(q=1, rootDirectory=True)

        if not is_subdir(scene_name, root_dir):
            raise RuntimeError("Maya workspace is not set correctly.")
