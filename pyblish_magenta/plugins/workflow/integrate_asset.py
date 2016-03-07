import os
import shutil
import cquery
import pyblish.api
import pyblish_magenta.api


class IntegrateAssets(pyblish.api.InstancePlugin):
    """Name and position instances on disk for assets

    This will integrate into the Assets' directory to: 
        {asset}/publish/{family}/{subset}/{version}

    Assumptions:
        - Each extracted instance is 1 file (no directories)

    Required context data:
        asset (str): Full path to current Asset

    Required instance data:
        name (str): Name of instance
        family (str): Name of family

    Optional instance data:
        subset (str): Name of subset

    """
    order = pyblish.api.IntegratorOrder

    label = "Asset"
    families = ["model", "rig", "pointcache", "review"]

    def process(self, instance):
        self.log.info("Integrating..")

        asset = instance.context.data.get("asset", None)
        assert asset, "Asset data must be present on context"
        assert os.path.isabs(asset), "Asset data must be absolute path"

        # New-style
        data = {
            "asset": asset,
            "instance": instance.data["name"],
            "family": instance.data["family"],
            "subset": instance.data.get("subset", "default")
        }

        data["assetName"] = os.path.basename(data["asset"])

        path = os.sep.join((
            "{asset}",
            "publish",
            "{family}",
            "{subset}")).format(**data)

        # Ensure unique version
        try:
            versions = os.listdir(path)
        except:
            versions = []

        next_version = pyblish_magenta.api.find_next_version(versions)
        data["version"] = pyblish_magenta.api.format_version(next_version)
        path = os.path.join(path, data['version'])

        # Store reference for upcoming plug-ins
        instance.data["integrationDir"] = path
        instance.data["integrationVersion"] = next_version  # 001

        # Integrate files from extractDir to integrationDir
        try:

            # Create version directory
            if not os.path.exists(path):
                os.makedirs(path)

            self.log.info("Moving files to %s" % path)

            tmp = instance.data["extractDir"]
            for src in (os.path.join(tmp, f) for f in os.listdir(tmp)):

                # TODO(marcus): Consider files without extension
                self.log.warning("integrating %s" % src)
                data["ext"] = src.split(".", 1)[-1]

                dst = os.path.join(path, "{assetName}_"
                                         "{family}_"
                                         "{instance}_"
                                         "{version}.{ext}".format(
                                            **data))
                self.log.info("\"%s\" -> \"%s\"" % (src, dst))
                shutil.copyfile(src, dst)

            cquery.tag(path, ".Version")
            self.log.debug("Tagged %s with .Version" % path)

            try:
                subset_path = os.path.dirname(path)
                cquery.tag(subset_path, ".Subset")
                self.log.debug("Tagged %s with .Subset" % subset_path)
            except cquery.TagExists:
                pass

        except OSError as e:
            # If, for whatever reason, this instance did not get written.
            instance.data.pop("integrationDir")
            raise e

        except Exception as e:
            raise Exception("An unknown error occured: %s" % e)
