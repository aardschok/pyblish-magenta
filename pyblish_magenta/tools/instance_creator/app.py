import sys
import contextlib

from Qt import QtWidgets, QtCore

import lib
import model


self = sys.modules[__name__]
self._window = None


class FamilyDescriptionWidget(QtWidgets.QWidget):
    """A family description widget.

    Shows a family icon, family name and a help description.
    Used in instance creator header.

     _________________
    |  ____           |
    | |icon| FAMILY   |
    | |____| help     |
    |_________________|

    """

    SIZE = 40

    def __init__(self, parent=None):
        super(FamilyDescriptionWidget, self).__init__(parent=parent)

        # Header font
        font = QtWidgets.QFont()
        font.setBold(True)
        font.setPointSize(14)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        icon = QtWidgets.QLabel()
        icon.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                           QtWidgets.QSizePolicy.Maximum)
        icon.setFixedWidth(40)
        icon.setFixedHeight(40)
        icon.setStyleSheet("""
        QLabel {
            padding-right: 5px;
        }
        """)

        label_layout = QtWidgets.QVBoxLayout()
        label_layout.setSpacing(0)

        family = QtWidgets.QLabel("family")
        family.setFont(font)
        family.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft)

        help = QtWidgets.QLabel("help")
        help.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        label_layout.addWidget(family)
        label_layout.addWidget(help)

        layout.addWidget(icon)
        layout.addLayout(label_layout)

        self.help = help
        self.family = family
        self.icon = icon

        # Store default fallback pixmap for icon
        icon = self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon)
        pixmap = icon.pixmap(self.SIZE, self.SIZE)
        pixmap = pixmap.scaled(self.SIZE, self.SIZE)
        self.fallback_pixmap = pixmap

    def set_family(self, family):
        """Update elements to display information of a family item.

        Args:
            family (dict): A family item as registered with name, help and icon

        Returns:
            None

        """
        if not family:
            return

        icon = family.get("icon", None)
        if icon:
            pixmap = icon.pixmap(self.SIZE, self.SIZE)
            pixmap = pixmap.scaled(self.SIZE, self.SIZE)
        else:
            pixmap = self.fallback_pixmap

        self.icon.setPixmap(pixmap)

        self.family.setText(family.get("name", "family"))
        self.help.setText(family.get("help", ""))


class CreateWidget(QtWidgets.QWidget):
    """Widget to create new instances"""

    closed = QtCore.Signal()

    def __init__(self, parent=None):
        super(CreateWidget, self).__init__(parent=parent)

        header = FamilyDescriptionWidget()
        body = QtWidgets.QWidget()
        lists = QtWidgets.QWidget()
        footer = QtWidgets.QWidget()

        list1Container = QtWidgets.QWidget()
        list2Container = QtWidgets.QWidget()

        model1 = model.FamiliesModel()
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

        list1Header = QtWidgets.QLabel("Family")
        list2Header = QtWidgets.QLabel("Subset")
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
        layout.addWidget(header)
        layout.addWidget(body)
        layout.addWidget(footer)

        self.header = header
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

    def refresh(self):

        self.model1.refresh()

        selection = self.list1.selectionModel()
        selection.setCurrentIndex(self.model1.index(0),
                                  selection.Select)

        self.list2.setCurrentItem(self.list2.item(0))

    def on_list1changed(self, current, previous):

        self.list2.clear()

        subsets = current.data(model.SubsetRole)
        for subset in subsets:
            item = QtWidgets.QListWidgetItem(subset)
            self.list2.addItem(item)

        family = current.data(model.NodeRole)
        self.header.set_family(family)

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
            self.closed.emit()


class ManageWidget(QtWidgets.QWidget):
    """Widget to manage current instances in the scene"""

    def __init__(self, parent=None):
        super(ManageWidget, self).__init__(parent=parent)

        instance_model = model.InstancesModel()
        instance_model.refresh()

        view = QtWidgets.QListView()
        view.setStyleSheet("""
            QListView::item{
                padding: 3px 5px;
            }
        """)
        view.setModel(instance_model)
        view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        refresh = QtWidgets.QPushButton("Refresh")
        add = QtWidgets.QPushButton("Add members")
        remove = QtWidgets.QPushButton("Remove members")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(refresh)
        layout.addWidget(view)
        layout.addWidget(add)
        layout.addWidget(remove)

        self.view = view
        self.model = instance_model

        # Connect slots
        refresh.clicked.connect(instance_model.refresh)
        add.clicked.connect(self.on_add_selected)
        remove.clicked.connect(self.on_remove_selected)
        view.doubleClicked.connect(self.on_double_click)
        view.customContextMenuRequested.connect(self.on_context_menu)

    def get_current(self):
        selection = self.view.selectionModel()
        return selection.currentIndex().data(model.NodeRole)

    def on_add_selected(self):
        """Add selection to members in the current instance"""

        from maya import cmds
        objset = self.get_current()['node']
        nodes = cmds.ls(sl=True)
        cmds.sets(nodes, forceElement=objset)

    def on_remove_selected(self):
        """Remove selection from members in the current instance"""

        from maya import cmds
        objset = self.get_current()['node']
        nodes = cmds.ls(sl=True)
        cmds.sets(nodes, remove=objset)

    def on_double_click(self, index):
        """Select the instance on double click"""

        from maya import cmds
        if not index.isValid():
            return

        item = index.data(model.NodeRole)
        cmds.select(item['node'], replace=True, noExpand=True)

    def on_context_menu(self, pos):

        from maya import cmds

        global_pos = self.view.mapToGlobal(pos)

        selection = self.view.selectionModel()
        current = selection.currentIndex()

        if not current.isValid():
            return

        item = current.data(model.NodeRole)

        menu = QtWidgets.QMenu()

        def on_select_instance():
            item = self.get_current()
            if not item:
                return

            node = item['node']
            cmds.select(node, replace=True, noExpand=True)

        def on_select_members():
            item = self.get_current()
            if not item:
                return

            node = item['node']
            members = cmds.sets(node, query=True)
            cmds.select(members, replace=True, noExpand=True)

        def on_delete():
            """Delete the current instance"""

            from maya import cmds
            objset = self.get_current()['node']
            cmds.delete(objset)
            self.model.refresh()

        select_instance = QtWidgets.QAction("Select Instance", self)
        select_instance.triggered.connect(on_select_instance)
        select_members = QtWidgets.QAction("Select Members", self)
        select_members.triggered.connect(on_select_members)
        delete = QtWidgets.QAction("Delete Instance", self)
        delete.triggered.connect(on_delete)

        menu.addAction(select_instance)
        menu.addAction(select_members)
        menu.addSeparator()
        menu.addAction(delete)

        action = menu.exec_(global_pos)
        return action


class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.setWindowTitle("Instance Creator")
        self.setObjectName("instanceCreator")

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Makes Maya perform magic which makes the window stay
        # on top in OS X and Linux. As an added bonus, it'll
        # make Maya remember the window position
        self.setProperty("saveWindowPref", True)

        tabs = QtWidgets.QTabWidget()

        create = CreateWidget()
        manage = ManageWidget()

        tabs.addTab(create, "Create")
        tabs.addTab(manage, "Manage")

        create.refresh()

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tabs)

        create.closed.connect(self.close)

    def keyPressEvent(self, event):
        """Custom keyPressEvent.

        Override keyPressEvent to do nothing so that Maya's panels won't
        take focus when pressing "SHIFT" whilst mouse is over viewport or
        outliner. This way users don't accidently perform Maya commands whilst
        trying to name an instance.

        """
        pass


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
