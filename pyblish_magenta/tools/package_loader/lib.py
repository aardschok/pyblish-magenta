import os
import json
import cquery


def list_packages(root):
    """Return dictionary of packages"""
    packages = dict()

    for package in cquery.matches(root, selector=".Package"):
        basename = os.path.basename(package)
        packages[basename] = {
            "path": package.replace("\\", "/"),
            "versions": {
                os.path.basename(version): version.replace("\\", "/")
                for version in cquery.matches(
                    package, selector=".Version")
                }
        }

    return packages


def load_package(path, representation):
    """Load package at `path`"""
    from maya import cmds

    try:
        pkg = next(f for f in os.listdir(path)
                   if f.endswith(".pkg"))
    except StopIteration:
        raise Exception("Package did not have a .pkg file; this is a bug")

    with open(os.path.join(path, pkg)) as f:
        pkg = json.load(f)

    print("Loading %s" % pkg)

    # Go to shot
    parent_item = cquery.first_match(path,
                                     selector=".Asset",
                                     direction=cquery.UP)

    # Find and load corresponding subsets
    subsets = {os.path.basename(subset): subset
               for subset in cquery.matches(parent_item, ".Subset")}

    for subset, version in pkg.iteritems():
        subset_path = subsets[subset]
        version_path = next(v for v in cquery.matches(subset_path, ".Version")
                            if os.path.basename(v) == version)

        try:
            fname = next(os.path.join(version_path, f)
                         for f in os.listdir(version_path)
                         if f.endswith(representation))
        except StopIteration:
            raise Exception("Package did not reference Alembic files; "
                            "this is a hardcoded behaviour (and bug)")

        namespace = subset + "_"
        reference_node = namespace + "RN"
        if cmds.objExists(reference_node):
            print("Updating not yet implemented")
        else:
            cmds.file(fname,
                      reference=True,
                      namespace=namespace)
