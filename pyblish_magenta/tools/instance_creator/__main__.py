import pyblish_magenta.tools.instance_creator.app

import pyblish_cb
pyblish_cb.setup()

with pyblish_magenta.tools.instance_creator.app.application():
    pyblish_magenta.tools.instance_creator.app.show()
