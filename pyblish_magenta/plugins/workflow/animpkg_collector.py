import pyblish.api


class CollectAnimPkg(pyblish.api.Collector):
    hosts = ["maya"]
    label = "Collect animPkg"
    order = pyblish.api.Collector.order + 0.1

    def process(self, context):
        pointcaches = [i.id for i in context
                       if i.data.get("family") == "pointcache"]

        if pointcaches:
            self.log.info("Found animPkg")

            instance = context.create_instance("animPkg")
            instance.data["family"] = "package"
            instance.data["label"] = "animation"
            instance.data["subset"] = "animPkg"

            self.log.info("Adding %s" % pointcaches)
            instance[:] = pointcaches
