import os
import json

import pyblish.api
import cquery
from pyblish_magenta.api import (
    format_version,
    compute_publish_directory,
    find_next_version
)


class BuildAnimPkg(pyblish.api.Plugin):
    """Tie subsets together into a new package"""

    label = "Build Animation Package"
    hosts = ["maya"]
    families = ["package"]
    category = "Build"
    order = pyblish.api.Integrator.order + 1

    destination_template = "{publish}/{subset}/{version}"
    filename_template = "{topic}_{subset}_{version}_{instance}"

    def process(self, context, instance):
        published_instances = [i.id for i in context if i.data("published")]
        animation_instances = [context[i] for i in instance
                               if i in published_instances]

        assert animation_instances, "No new animation was published"

        self.log.info("Looking for %s" % list(instance))
        self.log.info("Published instances: %s" % published_instances)
        self.log.info("Building animation "
                      "package from %s" % animation_instances)

        publish_dir = compute_publish_directory(
            context.data("currentFile").replace("\\", "/"))
        animpkg_dir = os.path.join(publish_dir, "animPkg")

        self.log.info("animPkg located at: %s" % animpkg_dir)

        try:
            animpkg_versions = sorted(os.listdir(animpkg_dir))
        except OSError:
            animpkg_versions = []

        self.log.info("animPkg versions found: %s" % animpkg_versions)

        package = {}
        if animpkg_versions:
            # Find existing subsets and their versions
            last_version_dir = os.path.join(animpkg_dir,
                                            animpkg_versions[-1])
            self.log.info("Looking up package file in %s" % last_version_dir)
            package_file = [os.path.join(last_version_dir, fname)
                            for fname in os.listdir(last_version_dir)
                            if fname.endswith(".pkg")][0]

            self.log.info("Reading from %s" % package_file)
            with open(package_file) as f:
                package = json.load(f)

        self.log.info("Using package data: %s" % package)
        for i in animation_instances:
            s = i.data("subset")
            v = i.data("integrationVersion")
            package[s] = format_version(v)

        self.log.info("New animPkg: %s" % package)

        version = find_next_version(animpkg_versions)

        dst = self.destination_template.format(**{
            "publish": publish_dir,
            "subset": instance.data("subset"),
            "version": format_version(version),
        }).replace("/", os.sep)

        topic = "_".join(os.environ["TOPICS"].split())
        name = self.filename_template.format(**{
            "topic": topic,
            "subset": instance.data("subset"),
            "version": format_version(version),
            "instance": instance.data("name")
        })

        try:
            os.makedirs(dst)
        except OSError:
            self.log.warning("Tried creating %s but failed" % dst)

        self.log.info("Writing new package to: %s" % dst)
        with open(os.path.join(dst, name) + ".pkg", "w") as f:
            json.dump(package, f, indent=2, sort_keys=True)

        self.log.info("Writing metadata to: %s" % dst)
        with open(os.path.join(dst, name) + ".meta", "w") as f:
            metadata = instance.data("metadata")
            self.log.info("Metadata: %s" % metadata)
            json.dump(metadata, f, indent=2, sort_keys=True)

        cquery.tag(dst, ".Version")

        try:
            cquery.tag(animpkg_dir, ".Package")
        except cquery.TagExists:
            pass
