from Qt import QtCore, QtWidgets
import lib

SubsetRole = QtCore.Qt.UserRole + 1
NodeRole = QtCore.Qt.UserRole + 2


class Model(QtCore.QAbstractListModel):
    """The Families model"""

    ROLES = {
        QtCore.Qt.DisplayRole: "name",
        QtCore.Qt.ToolTipRole: "help",
        QtCore.Qt.DecorationRole: "icon",
        SubsetRole: "subsets",
        NodeRole: None
    }

    def __init__(self, parent=None):
        super(Model, self).__init__(parent)
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

    def flags(self, index):

        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return (
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ToolTip
        )