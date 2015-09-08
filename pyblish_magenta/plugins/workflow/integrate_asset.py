import os
import shutil

import pyblish.api
import pyblish_magenta.api
from pyblish_magenta.vendor import cquery


class IntegrateAssets(pyblish.api.Integrator):
    """Name and position instances on disk for shots"""

    label = "Assets"
    families = ["model", "rig", "pointcache"]

    destination_template = "{publish}/{subset}/{version}"
    filename_template = "{topic}_{subset}_{version}_{instance}"

    def process(self, context, instance):
        if not instance.data("extractDir"):
            return self.log.debug("Skipping %s; no files found" % instance)

        self.log.debug("Source file: %s" % context.data("currentFile"))

        current_file = context.data("currentFile").replace("\\", "/")
        publish_dir = pyblish_magenta.api.compute_publish_directory(
            current_file)

        subset = instance.data("subset") or "default"

        # Compute version of this subset
        current_subsets = context.data("__currentSubsets__", {})

        subset_dir = "{publish}/{subset}".format(**{
            "publish": publish_dir,
            "subset": subset
        }).replace("/", os.sep)

        if subset in current_subsets:
            version = current_subsets[subset]
        else:
            version = self.compute_next_version(subset_dir)

        current_subsets[subset] = version
        context.set_data("__currentSubsets__", current_subsets)

        src = instance.data("extractDir")
        dst = self.destination_template.format(**{
            "publish": publish_dir,
            "subset": subset,
            "version": pyblish_magenta.api.format_version(version),
        }).replace("/", os.sep)

        self.log.info("Integrating %s -> %s" % (src, dst))

        topic = "_".join(os.environ["TOPICS"].split())
        name = self.filename_template.format(**{
            "topic": topic,
            "subset": subset,
            "version": pyblish_magenta.api.format_version(version),
            "instance": instance.data("name")
        })

        try:
            os.makedirs(subset_dir)
        except OSError:
            pass

        for fname in os.listdir(src):
            abs_src = os.path.join(src, fname)

            if os.path.isfile(abs_src):
                try:
                    os.makedirs(dst)
                except OSError:
                    pass

                _, ext = os.path.splitext(fname)
                filename = name + ext

                abs_dst = os.path.join(dst, filename)
                self.log.info("Copying file \"%s\" to \"%s\"" % (abs_src, dst))
                shutil.copy(abs_src, abs_dst)

            elif os.path.isdir(abs_src):
                abs_dst = os.path.join(dst, name, fname)
                self.log.info("Copying directory \"%s\" to \"%s\""
                              % (abs_src, abs_dst))
                shutil.copytree(abs_src, abs_dst)

            else:
                raise Exception("%s is not a valid path" % src)

        # Store reference for further integration
        instance.set_data("published", True)
        instance.set_data("integrationVersion", version)
        instance.set_data("integrationDir", dst)

        cquery.tag(dst, ".Version")
        try:
            cquery.tag(subset_dir, ".Subset")
        except cquery.TagExists:
            self.log.warning("%s already tagged" % subset_dir)

        self.log.info("Integrated to directory \"{0}\"".format(dst))

    def compute_next_version(self, versions_dir):
        try:
            existing_versions = os.listdir(versions_dir)
            version = pyblish_magenta.api.find_next_version(existing_versions)
        except OSError:
            version = 1

        return version
