import sys
import contextlib

from Qt import QtWidgets, QtCore

import lib
from model import Model


self = sys.modules[__name__]
self._window = None


class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Instance Creator")

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        body = QtWidgets.QWidget()
        lists = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        list1Container = QtWidgets.QWidget()
        list2Container = QtWidgets.QWidget()

        model1 = Model()
        list1 = QtWidgets.QListView()
        list1.setModel(model1)
        list1.setStyleSheet("""
            QListView::item{
                padding: 3px 5px;
            }
        """)
        list1.setSelectionMode(list1.SingleSelection)
        list1.setSelectionBehavior(list1.SelectRows)

        list2 = QtWidgets.QListWidget()

        header_font = QtWidgets.QFont()
        header_font.setBold(True)
        header_font.setPointSize(10)

        list1Header = QtWidgets.QLabel("Family")
        list1Header.setFont(header_font)
        list2Header = QtWidgets.QLabel("Subset")
        list2Header.setFont(header_font)
        subset_fld = QtWidgets.QLineEdit()

        layout = QtWidgets.QVBoxLayout(list1Container)
        layout.addWidget(list1Header)
        layout.addWidget(list1)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(list2Container)
        layout.addWidget(list2Header)
        layout.addWidget(subset_fld)
        layout.addWidget(list2)
        layout.setContentsMargins(0, 0, 0, 0)

        options = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(options)
        layout.setContentsMargins(0, 0, 0, 0)

        useselection_chk = QtWidgets.QCheckBox("Use selection")
        useselection_chk.setCheckState(QtCore.Qt.Checked)
        layout.addWidget(useselection_chk, 0, 0)

        autoclose_chk = QtWidgets.QCheckBox("Close after creation")
        autoclose_chk.setCheckState(QtCore.Qt.Checked)
        layout.addWidget(autoclose_chk, 1, 0)

        layout = QtWidgets.QHBoxLayout(lists)
        layout.addWidget(list1Container)
        layout.addWidget(list2Container)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(body)
        layout.addWidget(lists)
        layout.addWidget(options, 0, QtCore.Qt.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        
        create_btn = QtWidgets.QPushButton("Create")

        layout = QtWidgets.QHBoxLayout(footer)
        layout.addWidget(create_btn)
        layout.setContentsMargins(0, 0, 0, 0)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(body)
        layout.addWidget(footer)

        self.create_btn = create_btn
        self.subset_fld = subset_fld
        self.model1 = model1
        self.list1 = list1
        self.list2 = list2
        self.useselection_chk = useselection_chk
        self.autoclose_chk = autoclose_chk

        create_btn.clicked.connect(self.on_create)
        selection = list1.selectionModel()
        selection.currentChanged.connect(self.on_list1changed)
        list2.currentItemChanged.connect(self.on_list2changed)

        self.resize(350, 250)

    def keyPressEvent(self, event):
        """Custom keyPressEvent.

        Override keyPressEvent to do nothing so that Maya's panels won't
        take focus when pressing "SHIFT" whilst mouse is over viewport or
        outliner. This way users don't accidently perform Maya commands whilst
        trying to name an instance.

        """
        pass

    def refresh(self):

        self.model1.refresh()

        selection = self.list1.selectionModel()
        selection.setCurrentIndex(self.model1.index(0),
                                  selection.Select)

        self.list2.setCurrentItem(self.list2.item(0))

    def on_list1changed(self, current, previous):

        self.list2.clear()

        subsets = current.data(QtCore.Qt.UserRole + 1)
        for subset in subsets:
            item = QtWidgets.QListWidgetItem(subset)
            self.list2.addItem(item)

        self.list2.setCurrentItem(self.list2.item(0))

    def on_list2changed(self, current, previous):
        if not current:
            return

        self.subset_fld.setText(current.text())

    def on_create(self):

        selection = self.list1.selectionModel()
        family = selection.currentIndex().data(QtCore.Qt.DisplayRole)
        subset = self.subset_fld.text()

        use_selection = self.useselection_chk.checkState()
        lib.create(family, subset, use_selection)

        if self.autoclose_chk.checkState():
            self.close()


def show():
    if self._window:
        self._window.close()
        del(self._window)

    try:
        widgets = QtWidgets.QApplication.topLevelWidgets()
        widgets = dict((w.objectName(), w) for w in widgets)
        parent = widgets['MayaWindow']
    except KeyError:
        parent = None

    window = Window(parent)
    window.show()
    window.refresh()

    self._window = window


@contextlib.contextmanager
def application():
    app = QtWidgets.QApplication(sys.argv)
    yield
    app.exec_()


if __name__ == '__main__':

    def main():
        """Use case example test"""

        import lib

        families = [
            {
                "name": "model",
                "subsets": ["default", "hires", "lowres"],
                "help": "A model (geo + curves) without history"
            },
            {
                "name": "rig",
                "subsets": ["rigAnim", "rigSimCloth", "rigSimFur"],
                "help": "Artist-friendly rig with controls to direct motion"
            },
            {
                "name": "look",
                "subsets": ["default", "blue", "red"],
                "help": "Shader connections that define a look for shapes"
            }
        ]

        for f in families:
            lib.register_family(f)

        with application():
            show()

    main()
