import os
import datetime
import pyblish.api


class LogHistory(pyblish.api.ContextPlugin):
    """A Log of the current Publish will be produced.

    Only information up to the `order` is collected.

    Logs are stored in the user folder in a `logs`
    directory.

    """

    label = "Log History"
    order = pyblish.api.ValidatorOrder + 0.45
    optional = True

    def process(self, context):
        self.log.debug("Logging history for %s" % context.data["user"])

        time = datetime.datetime.utcnow().isoformat().rsplit(".")[0]
        time = time.replace("T", ".")
        output = "Published from \"%s\"..\n" % context.data["currentFile"]
        output += "Time: %s\n" % time

        output += "\n# Plug-ins\n"
        output += "\n"

        # List plug-ins
        output += "{:<10}{:<40} -> {}\n".format(
            "Success", "Plug-in", "Instance")
        output += "-" * 70
        for result in context.data["results"]:
            output += "\n{success:<10}{plugin:<40} -> {instance}".format(**{
                "success": "True" if result["success"] else "False",
                "instance": result["instance"] or "Context",
                "plugin": result["plugin"].label or result["plugin"].__name__
            })

        # List instances
        output += "\n\n"
        output += "# Instances\n"
        for i, instance in enumerate(context):
            output += "\n- %i: \"%s\"" % (i, instance.data["name"])

            for key, value in instance.data.iteritems():
                # Trim advanced content
                if isinstance(value, (dict, list)):
                    key += " (%i)" % len(value)

                if not isinstance(value, (basestring, int, float, bool)):
                    value = "..."

                output += "\n  - {key}: {value}".format(key=key, value=value)

        time = pyblish.api.format_filename(time)
        basename = os.path.basename(context.data["currentFile"])
        name, _ = os.path.splitext(basename)
        fname = "%s.%s.txt" % (time, name)
        dirname = os.path.expanduser("~/logs")
        path = os.path.join(dirname, fname)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(path, "w") as f:
            f.write(output)
