import pyblish
import pyblish_magenta.api


class ValidateRigControlsNoAnimation(pyblish.api.InstancePlugin):
    """Ensure no keyframes on controls in the rig Instance.

    """

    order = pyblish_magenta.api.ValidateContentsOrder
    label = "Controls No Animation"
    hosts = ["maya"]
    families = ["rig"]
    optional = True

    def process(self, instance):
        from maya import cmds

        # TODO: Check incoming connections (parent constraints, etc.) instead of animCurves
        # TODO: Check only keyable attributes?
        # TODO: Check only unlocked attributes?

        # Get the controls set from the instance
        sets = cmds.ls(instance, type='objectSet')
        controls_sets = []
        for s in sets:
            if s.endswith("controls_SET"):
                controls_sets.append(s)

        if not controls_sets:
            raise RuntimeError("No controls_SET in instance")

        controls_set = controls_sets[0]

        members = cmds.sets(controls_set, q=1)
        curves = cmds.keyframe(members, q=1, name=True)
        if curves:
            invalid = list(set(cmds.listConnections(curves)))
            raise RuntimeError("Keyframes found: {0}".format(invalid))
