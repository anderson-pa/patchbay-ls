import pandas as pd
from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex


class PandasModel(QAbstractTableModel):
    """Modified from https://github.com/eyllanesc/stackoverflow/blob/master/questions/44603119/PandasModel.py"""  # noqa

    def __init__(self, df=pd.DataFrame(), parent=None):
        QAbstractTableModel.__init__(self, parent=parent)
        self._df = df
        self._column_formats = {}

    def update(self, df):
        self._df = df

    def set_column_format(self, column, format_str):
        self._column_formats[column] = format_str

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]

            except (IndexError,):
                return None
        elif orientation == Qt.Vertical:
            try:
                return self._df.index.tolist()[section]
            except (IndexError,):
                return None

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if not index.isValid():
            return None

        return format(self._df.ix[index.row(), index.column()],
                      self._column_formats.get(index.column(), ''))

    def setData(self, index, value, role=Qt.EditRole):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            print('has topyobject')
            value = value.toPyObject()
        else:
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order=Qt.AscendingOrder):
        col_name = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(col_name, inplace=True,
                             ascending=(order == Qt.AscendingOrder))
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()

    # def flags(self, index):
    #     return Qt.ItemIsEnabled
