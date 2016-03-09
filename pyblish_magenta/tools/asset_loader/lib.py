import os
from pyblish_magenta.vendor import cquery


def load(root, representation=".ma"):
    """Load file at `root`"""
    from maya import cmds

    fname = next(os.path.join(root, f)
                 for f in os.listdir(root)
                 if f.endswith(representation))

    asset = cquery.first_match(root,
                               selector=".Asset",
                               direction=cquery.UP)
    asset = os.path.basename(asset)

    subset = cquery.first_match(root,
                                selector=".Subset",
                                direction=cquery.UP)
    subset = os.path.basename(subset)

    def namespace(version):
        namespace = asset
        if subset != "default":
            namespace += "_%s" % subset
        return namespace + "%02d_" % version

    version = 1
    reference_node = namespace(version) + "RN"
    while cmds.objExists(reference_node):
        version += 1
        reference_node = namespace(version) + "RN"

    cmds.file(fname,
              reference=True,
              namespace=namespace(version))


def representations(root):
    return list(os.path.splitext(f)[-1] for f in os.listdir(root))
