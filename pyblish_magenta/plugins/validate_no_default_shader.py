import pyblish.api
from maya import cmds


class ValidateNoDefaultShader(pyblish.api.Validator):
    """ Validates that none of the nodes in the instance have any keys """
    families = ['lookdev']
    hosts = ['maya']
    optional = True
    version = (0, 1, 0)

    _default_shading_engines = ['initialShadingGroup', 'initialParticleSE']

    def process(self, instance):
        """Process all the nodes in the instance """
        if not instance:
            return

        invalid = []

        shaders = cmds.ls(instance, type='shadingEngine')
        if shaders:
            for shader in shaders:
                if shader in self._default_shading_engines:
                    invalid.append(shader)

        if invalid:
            raise ValueError("Default shaders found: {0}".format(invalid))