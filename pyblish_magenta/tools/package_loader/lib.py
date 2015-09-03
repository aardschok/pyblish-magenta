import os
import json
import cquery


def list_packages(root):
    """Return dictionary of packages"""
    packages = dict()
    parent_item = cquery.first_match(root,
                                     selector=".Item",
                                     direction=cquery.UP)
    if cquery.has_class(parent_item, ".Shot"):
        for package in cquery.matches(parent_item, selector=".Package"):
            basename = os.path.basename(package)
            packages[basename] = {
                "path": package.replace("\\", "/"),
                "versions": {
                    os.path.basename(version): version.replace("\\", "/")
                    for version in cquery.matches(
                        package, selector=".Version")
                    }
            }

    else:
        raise Exception("%s is not a shot" % root)

    return packages


def load_package(path):
    """Load package at `path`"""
    from maya import cmds

    pkg = next(f for f in os.listdir(path)
               if f.endswith(".pkg"))

    with open(os.path.join(path, pkg)) as f:
        pkg = json.load(f)

    # Go to shot
    parent_item = cquery.first_match(path,
                                     selector=".Item",
                                     direction=cquery.UP)

    # Find and load corresponding subsets
    subsets = {os.path.basename(subset): subset
               for subset in cquery.matches(parent_item, ".Subset")}

    for subset, version in pkg.iteritems():
        subset_path = subsets[subset]
        version_path = next(v for v in cquery.matches(subset_path, ".Version")
                            if os.path.basename(v) == version)
        fname = next(os.path.join(version_path, f)
                     for f in os.listdir(version_path)
                     if f.endswith(".ma"))

        fname.replace(os.environ.get("PROJECTROOT", "$$$"),
                      "$PROJECTROOT")

        namespace = subset + "_"
        reference_node = namespace + "RN"
        if cmds.objExists(reference_node):
            print("Updating not yet implemented")
        else:
            cmds.file(fname,
                      reference=True,
                      namespace=namespace)
