import os
import sys

from PySide import QtCore, QtGui
from maya import cmds

from pyblish_magenta.tools.asset_loader import app

self = sys.modules[__name__]
self._window = None


class Window(app.Window):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        self.btn_load.setText("Assign")

    def on_load(self):
        from pyblish_magenta.vendor import cquery
        item = self.list5.currentItem()
        versiondir = item.data(QtCore.Qt.UserRole + 1)
        asset = cquery.first_match(versiondir, ".Asset", direction=cquery.UP)

        # p:/myproject/assets/myasset
        publish = os.path.join(asset, "publish")

        # looks/default/v001
        identifier = versiondir.split(publish)[-1][1:].replace("\\", "/")
        print("Setting %s" % identifier)

        shader_relations = iter(os.listdir)

        selection = cmds.ls(sl=True)
        for node in selection + cmds.listRelatives(selection, shapes=True):
            cmds.setAttr(node + ".cbShaderVariation",
                         identifier,
                         type="string")


def show(root, representation):
    if self._window:
        self._window.refresh(root, representation)
        return self._window.show()

    widgets = QtGui.QApplication.topLevelWidgets()
    widgets = dict((w.objectName(), w) for w in widgets)
    parent = widgets['MayaWindow']

    root = os.path.realpath(root)
    window = Window(parent)
    window.show()
    window.refresh(root, representation)

    self._window = window
    return window


if __name__ == '__main__':
    import cquery
    root = r"P:\Projects\KLM_Bluey"
    root = cquery.first_match(root,
                              selector=".Project",
                              direction=cquery.UP)
    root = os.path.join(root, "production", "assets")

    with app.application():
        show(root, representation=".mb")
