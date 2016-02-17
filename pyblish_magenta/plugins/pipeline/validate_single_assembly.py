import pyblish.api


class ValidateSingleAssembly(pyblish.api.Validator):
    """Ensure all nodes are in a single assembly

    Published assets must be contained within a single transform
    at the root of your outliner.

    """

    families = ['rig', 'model']
    hosts = ['maya']
    category = 'rig'
    version = (0, 1, 0)
    label = 'Single Assembly'

    def process(self, instance):
        from maya import cmds

        assemblies = cmds.ls(instance, assemblies=True)

        # ensure unique (somehow `maya.cmds.ls` doesn't manage that)
        assemblies = set(assemblies)

        assert len(assemblies) > 0, (
            "One assembly required for %s" % instance)
        assert len(assemblies) < 2, (
            'Multiple assemblies found: %s' % assemblies)
