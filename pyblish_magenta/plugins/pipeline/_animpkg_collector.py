import pyblish.api


class CollectAnimPkg(pyblish.api.ContextPlugin):
    hosts = ["maya"]
    label = "Collect animPkg"
    order = pyblish.api.Collector.order + 0.1

    def process(self, context):

        # Collect pointcache object sets
        pointcaches = list()
        for instance in context:
            if instance.data["family"] != "pointcache":
                continue

            object_set = instance.data.get('objSetName', None)
            if not object_set:
                continue

            pointcaches.append(object_set)

        if pointcaches:
            self.log.info("Found animPkg")

            instance = context.create_instance("animPkg")
            instance.data["family"] = "package"
            instance.data["label"] = "animation"
            instance.data["subset"] = "animPkg"

            self.log.info("Adding %s" % pointcaches)
            instance[:] = pointcaches
