from Qt import QtCore, QtWidgets
import lib

SubsetRole = QtCore.Qt.UserRole + 1
NodeRole = QtCore.Qt.UserRole + 2
StateRole = QtCore.Qt.UserRole + 3


class FamiliesModel(QtCore.QAbstractListModel):
    """The Families model"""

    ROLES = {
        QtCore.Qt.DisplayRole: "name",
        QtCore.Qt.ToolTipRole: "help",
        QtCore.Qt.DecorationRole: "icon",
        SubsetRole: "subsets",
        NodeRole: None
    }

    def __init__(self, parent=None):
        super(FamiliesModel, self).__init__(parent)
        self.items = list()

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if role == NodeRole:
            return self.items[index.row()]

        if role in self.ROLES:
            item = self.items[index.row()]
            key = self.ROLES[role]
            return item.get(key, None)

    def append(self, item):
        self.beginInsertRows(QtCore.QModelIndex(),
                             self.rowCount(),
                             self.rowCount())
        self.items.append(item)
        self.endInsertRows()

    def rowCount(self, parent=None):
        return len(self.items)

    def refresh(self):

        self.items[:] = list()
        for family in sorted(lib.families, key=lambda i: i["name"]):
            self.append(family)


class InstancesModel(QtCore.QAbstractListModel):
    """The Instances model

    Lists the currently available instances in the scene.

    """

    ROLES = {
        QtCore.Qt.ToolTipRole: "help",
        QtCore.Qt.DecorationRole: "icon",
        SubsetRole: "subset",
        StateRole: "publish"
    }

    def __init__(self, parent=None):
        super(InstancesModel, self).__init__(parent)
        self.items = list()

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if not index.isValid():
            return

        item = self.items[index.row()]

        if role == QtCore.Qt.DisplayRole:
            family = item.get("family", None)
            subset = item.get("subset", None)
            return "{0} ({1})".format(subset, family)

        if role == NodeRole:
            return item

        if role in self.ROLES:
            key = self.ROLES[role]
            return item.get(key, None)

    def append(self, item):
        self.beginInsertRows(QtCore.QModelIndex(),
                             self.rowCount(),
                             self.rowCount())
        self.items.append(item)
        self.endInsertRows()

    def rowCount(self, parent=None):
        return len(self.items)

    def refresh(self):

        self.beginResetModel()
        self.items[:] = list()
        for inst in sorted(lib.ls(), key=lambda i: i["name"]):

            # Collect the icon from the registered families
            family = inst.get("family", None)
            icon = None
            for registered_family in lib.families:
                if registered_family['name'] == family:
                    icon = registered_family.get("icon", None)
                    break
            inst['icon'] = icon

            self.append(inst)
        self.endResetModel()
