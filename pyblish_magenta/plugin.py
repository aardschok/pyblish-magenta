import tempfile
import pyblish.api


class Extractor(pyblish.api.InstancePlugin):
    """Extractor base class.

    The extractor base class implements a "temp_dir" function used to generate
    a temporary directory for an instance to extract to.

    This temporary directory is generated through `tempfile.mkdtemp()`

    """
    order = pyblish.api.ExtractorOrder

    def temp_dir(self, instance):
        """Provide a temporary directory in which to store extracted files"""
        extract_dir = instance.data.get('extractDir', None)

        if not extract_dir:
            extract_dir = tempfile.mkdtemp()
            instance.data['extractDir'] = extract_dir

        return extract_dir


class Integrator(pyblish.api.InstancePlugin):
    """Integrator base class.

    The Integrator will raise a RuntimeError whenever the plugin is processed
    and previous plug-ins have given error results for this instance.

    This means integration will only take place if up to this point in time
    all of publishing was successful and had no errors.

    Note:
        When subclassing from this Integrator ensure to call this class'
        process method using, for example for your CustomIntegrator class:
            super(CustomIntegrator, self).process(instance)

    """
    order = pyblish.api.IntegratorOrder

    def process(self, instance):
        """

        Raises an error if any errors have occurred for this instance before
        this plug-in.

        This does not integrate the file, that is up to the subclassed plug-in.

        """

        context = instance.context
        results = context.data['results']

        # Get the errored instances
        errored_instances = []
        for result in results:
            if result["error"] is not None and result["instance"] is not None:
                if result["error"]:
                    instance = result["instance"]
                    errored_instances.append(instance)

        if instance in errored_instances:
            raise RuntimeError("Skipping because of errors being present for"
                               " this instance before Integration: "
                               "{0}".format(instance))
