from . import lib


def register_family(family, defaults, description=None):
    lib.families[family] = defaults