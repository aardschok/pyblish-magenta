import os
import json

import cquery
import pyblish.api
from pyblish_magenta.api import (
    format_version,
    find_next_version
)

conversions = {
    'animation': 'film',
    'comp': 'film',
    'lighting': 'film',
    'fx': 'film',
    'grooming': 'assets',
    'lookDev': 'assets',
    'modeling': 'assets',
    'rigging': 'assets',
    'editing': 'edit',  # unused?
    'audio': 'audio',  # unused?
}


class BuildAnimPkg(pyblish.api.Plugin):
    """Tie subsets together into a new package"""

    label = "Build Animation Package"
    hosts = ["maya"]
    families = ["package"]
    category = "Build"
    order = pyblish.api.Integrator.order + 1

    destination_template = "{publish}/{subset}/{version}"
    filename_template = "{subset}_{version}_{instance}"

    def process(self, context, instance):
        # Instances with an integration dir is assumed to have been published.
        all_published_instances = [i.id
                                   for i in context
                                   if "integrationDir" in i.data]

        # Convert string to Instance object from context.
        all_animation_instances = [context[i]
                                   for i in all_published_instances]

        # Only produce package if at least 1 new animation was published.
        if not all_animation_instances:
            return self.log.warning("No new animation was published")

        self.log.info("Looking for %s" % list(instance))
        self.log.info("Published instances: %s" % all_published_instances)
        self.log.info("Building animation "
                      "package from %s" % all_animation_instances)

        data = context.data["currentAssetInfo"].copy()

        packages_dir = os.path.join(data["asset"], ".packages")
        animpkg_dir = os.path.join(packages_dir, "animPkg")

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

        # Produce package
        # {
        #  "animation Bluey01": "v009",
        #  "animation Mom01": "v006"
        # }
        #
        for i in all_animation_instances:
            s = i.data["subset"]
            v = i.data["integrationVersion"]
            package[s] = format_version(v)

        self.log.info("New animPkg: %s" % package)

        version = find_next_version(animpkg_versions)

        dst = self.destination_template.format(**{
            "publish": packages_dir,
            "subset": instance.data["subset"],
            "version": format_version(version),
        }).replace("/", os.sep)

        name = self.filename_template.format(**{
            "subset": instance.data["subset"],
            "version": format_version(version),
            "instance": instance.data["name"]
        })

        try:
            os.makedirs(dst)
        except OSError as e:
            self.log.warning("Tried creating %s but failed" % dst)
            raise e

        self.log.info("Writing new package to: %s" % dst)
        with open(os.path.join(dst, name) + ".pkg", "w") as f:
            json.dump(package, f, indent=2, sort_keys=True)

        cquery.tag(dst, ".Version")

        try:
            cquery.tag(animpkg_dir, ".Package")
        except cquery.TagExists:
            pass
