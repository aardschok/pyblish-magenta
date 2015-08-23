
from PySide import QtGui
import pymel.core as pm
import os


def get_maya_main_window():
    """Return Maya's main window as a QWidget"""
    import maya.OpenMayaUI
    from shiboken import wrapInstance
    pointer = maya.OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(pointer), QtGui.QWidget)


def get_entity_name(reference_path):
    """Return the entity name from the first directory inside project root"""
    if 'PROJECTROOT' not in os.environ:
        return 'asset'  # temporary fallback

    path = os.path.realpath(reference_path)
    root = os.path.realpath(os.environ['PROJECTROOT'])
    relative = os.path.relpath(path, root)
    first_dir = relative.split(os.sep, 1)[0]
    return first_dir


def get_item_name(reference_path):
    instance = os.path.dirname(reference_path)
    family = os.path.dirname(instance)
    version = os.path.dirname(family)
    published = os.path.dirname(version)
    task = os.path.dirname(published)
    item = os.path.dirname(task)
    return os.path.basename(item)


def get_versions(filename):
    # NOTE(marcus): This should be based on something more
    # flexible than a fixed number of levels up a hierarchy.
    version_dir = os.path.realpath(os.path.join(filename, "..", "..", ".."))
    versions_dir = os.path.realpath(os.path.join(version_dir, ".."))
    versions = sorted(os.listdir(versions_dir))

    current_version = os.path.basename(version_dir)

    return current_version, versions


class ReferenceItemWidget(QtGui.QWidget):
    """The Widget used for a single reference in the ReferenceListWidget"""
    def __init__(self, reference):
        super(ReferenceItemWidget, self).__init__()
        self._reference = reference

        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)

        self.loaded = QtGui.QCheckBox()
        self.loaded.setFixedWidth(25)

        self.container_label = QtGui.QLabel()
        self.container_label.setSizePolicy(QtGui.QSizePolicy.Minimum,
                                           QtGui.QSizePolicy.MinimumExpanding)
        self.container_label.setStyleSheet("font: italic;")

        self.label = QtGui.QLabel()
        self.label.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                 QtGui.QSizePolicy.MinimumExpanding)
        self.label.setStyleSheet("font-weight: bold;")

        self.unresolved_path = QtGui.QLabel()
        self.unresolved_path.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                           QtGui.QSizePolicy.MinimumExpanding)
        self.unresolved_path.setStyleSheet("font-size: 10px;")

        self.version = QtGui.QComboBox()
        self.version.setFixedWidth(50)

        self.layout.addWidget(self.loaded)
        self.layout.addWidget(self.container_label)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.unresolved_path)
        self.layout.addWidget(self.version)

    def refresh(self):
        filename = self._reference.path

        state = self._reference.isLoaded()
        self.loaded.setChecked(state)

        # type of entity (eg. "asset" or "film")
        entity = get_entity_name(filename)
        self.container_label.setText(entity)

        # item
        item = get_item_name(filename)
        self.label.setText(item)

        # unresolved path
        self.unresolved_path.setText(self._reference.unresolvedPath())

        # version
        current_version, versions = get_versions(filename)
        self.version.clear()
        self.version.addItems(versions)
        self.version.setCurrentIndex(versions.index(current_version))

    def apply(self):
        """Apply the current state of the Item"""

        # Update loaded state
        if self.loaded.isChecked() != self._reference.isLoaded():
            if self.loaded.isChecked():
                self._reference.load()
            else:
                self._reference.unload()

        # Change version state
        filename = self._reference.path
        current_version, versions = get_versions(filename)

        chosen_version = self.version.currentText()
        if chosen_version != current_version:
            # TODO: Load other version correctly
            new_filename = filename.replace(current_version, chosen_version)

            # Include environment variables.
            # NOTE(marcus): This is essential, but
            # will need to be made more forgiving.
            new_filename = new_filename.replace(
                os.environ["PROJECTROOT"], "$PROJECTROOT")

            self._reference.replaceWith(new_filename)


class ReferenceListWidget(QtGui.QListWidget):
    """A Widget that holds a list of references"""

    def update(self):
        """Clear and load all current references in the scene"""
        self.clear()
        for reference in pm.getReferences(recursive=False).values():
            item = QtGui.QListWidgetItem()
            widget = ReferenceItemWidget(reference)

            item.setSizeHint(widget.sizeHint())

            # Add the item to the list with the widget
            self.addItem(item)
            self.setItemWidget(item, widget)

        self.refresh()

    def refresh(self):
        """Trigger a refresh on the widgets in the list"""
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            widget.refresh()

    def apply(self):
        """Trigger an apply on the widgets in the list"""
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            widget.apply()


class ReferenceManagerGUI(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(ReferenceManagerGUI, self).__init__(*args, **kwargs)

        self.setWindowTitle("Reference Manager")

        self.widget = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.reference_list = ReferenceListWidget()
        self.layout.addWidget(self.reference_list)
        self.reference_list.update()

        # Bottom button row
        self.bottom_buttons = QtGui.QHBoxLayout()
        self.update_all_button = QtGui.QPushButton("Update All")
        self.update_all_button.setFixedWidth(75)
        self.refresh_button = QtGui.QPushButton("Refresh")
        self.refresh_button.setFixedWidth(75)
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setFixedWidth(75)

        self.bottom_buttons.addStretch(0)
        self.bottom_buttons.addWidget(self.update_all_button)
        self.bottom_buttons.addWidget(self.refresh_button)
        self.bottom_buttons.addWidget(self.apply_button)

        self.refresh_button.clicked.connect(self.reference_list.refresh)
        self.apply_button.clicked.connect(self.reference_list.apply)

        self.layout.addLayout(self.bottom_buttons)


def maya():
    maya_window = get_maya_main_window()
    gui = ReferenceManagerGUI(parent=maya_window)
    gui.show()