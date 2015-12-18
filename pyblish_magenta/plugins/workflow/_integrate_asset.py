import os
import shutil
import cquery
import pyblish.api
import pyblish.util
import pyblish_magenta.api


class IntegrateAssets(pyblish.api.Integrator):
    """Name and position instances on disk for shots

    Assumptions:
        - Each extracted instance is 1 file (no directories)

    """

    label = "Assets"
    families = ["model", "rig", "pointcache", "proxy", "vrmeshReplace"]

    def process(self, context, instance):
        self.log.info("Integrating..")

        # New-style
        data = context.data["currentAssetInfo"]
        data.update({
            "subset": instance.data.get("subset", "default"),
            "instance": instance.data["name"]
        })

        path = os.sep.join((
            "{asset}",
            "publish",
            "{subset}")).format(**data)

        self.log.debug("Using new-style folder structure")

        # Ensure unique version
        try:
            versions = os.listdir(path)
        except:
            versions = []

        next_version = pyblish_magenta.api.find_next_version(versions)
        path = os.path.join(
            path, pyblish_magenta.api.format_version(next_version))

        # Store reference for upcoming plug-ins
        instance.data["integrationDir"] = path
        instance.data["integrationVersion"] = next_version  # 001
        data["version"] = pyblish_magenta.api.format_version(next_version)

        try:
            if not os.path.exists(path):
                os.makedirs(path)

            self.log.info("Moving files to %s" % path)

            tmp = instance.data["extractDir"]
            for src in (os.path.join(tmp, f) for f in os.listdir(tmp)):

                # TODO(marcus): Consider files without extension
                self.log.warning("integrating %s" % src)
                data["ext"] = src.split(".", 1)[-1]
                data["assetName"] = os.path.basename(data["asset"])
                data["taskName"] = os.path.basename(data["task"])

                # Subset may contain subdirectories
                data["subsetName"] = data["subset"].replace("/", "_")

                dst = os.path.join(path, "{assetName}_"
                                         "{taskName}_"
                                         "{subsetName}_"
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

        finally:
            # Backwards compatibility
            for key, selector in {"asset": ".Asset",
                                  "task": ".Task"}.iteritems():
                try:
                    cquery.tag(data[key], selector)
                except:
                    pass
